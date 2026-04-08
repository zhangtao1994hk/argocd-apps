import os
import logging
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pymysql
from datetime import datetime, timezone
import redis
from werkzeug.security import generate_password_hash, check_password_hash



logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s : %(message)s')
logger = logging.getLogger("dao-service")

app = Flask(__name__)

# 2. 数据库配置
# 生产环境建议通过环境变量注入，这里提供默认值
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "777777")
DB_HOST = os.getenv("DB_HOST", "mysql.middleware.svc.cluster.local")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
# 你的 mysql chart 只负责起实例，不一定会预先创建数据库；这里默认 appdb，并在启动时自动创建
DB_NAME = os.getenv("DB_NAME", "appdb")
PORT = int(os.getenv("PORT", 5000)) # 从环境变量读取端口，默认5000

# Redis 配置
REDIS_HOST = os.getenv("REDIS_HOST", "redis-svc.middleware.svc.cluster.local")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "666666")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

def ensure_database_exists():
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            charset="utf8mb4",
            connect_timeout=5,
        )
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4")
        conn.commit()
        conn.close()
        logger.info("Ensured database exists: %s", DB_NAME)
    except Exception as e:
        logger.error("Failed to ensure database exists: %s", e)

ensure_database_exists()

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Redis 连接
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
    decode_responses=True
)

def utcnow():
    return datetime.now(timezone.utc)


# 3. 表结构（DAO 只做数据存取，不做业务逻辑）
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    price_cents = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)


class Inventory(db.Model):
    __tablename__ = "inventory"
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32), nullable=False, default="CREATED")  # CREATED|PAID|CANCELLED
    subtotal_cents = db.Column(db.Integer, nullable=False, default=0)
    discount_cents = db.Column(db.Integer, nullable=False, default=0)
    total_cents = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price_cents = db.Column(db.Integer, nullable=False)
    line_total_cents = db.Column(db.Integer, nullable=False)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

# 初始化表
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize DB: {e}")

def money_to_cents(value):
    # Accept int cents or numeric string; keep minimal and predictable.
    if value is None:
        raise ValueError("missing value")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value * 100))
    if isinstance(value, str):
        # allow "12.34" or "1234"
        if "." in value:
            return int(round(float(value) * 100))
        return int(value)
    raise ValueError("invalid money type")


def product_to_dict(p: Product, inv_qty=None):
    out = {
        "id": p.id,
        "sku": p.sku,
        "name": p.name,
        "price_cents": p.price_cents,
    }
    if inv_qty is not None:
        out["stock"] = inv_qty
    return out


# 4. DAO API（给 backend 用）
@app.route("/products", methods=["GET"])
def list_products():
    products = Product.query.order_by(Product.id.asc()).all()
    inv_map = {i.product_id: i.quantity for i in Inventory.query.all()}
    return jsonify([product_to_dict(p, inv_map.get(p.id, 0)) for p in products])


@app.route("/products", methods=["POST"])
def create_product():
    data = request.get_json(silent=True) or {}
    try:
        sku = (data.get("sku") or "").strip()
        name = (data.get("name") or "").strip()
        price_cents = money_to_cents(data.get("price_cents"))
        stock = int(data.get("stock", 0))
        if not sku or not name or price_cents < 0 or stock < 0:
            return jsonify({"error": "invalid payload"}), 400

        if Product.query.filter_by(sku=sku).first() is not None:
            return jsonify({"error": "sku already exists"}), 409

        p = Product(sku=sku, name=name, price_cents=price_cents)
        db.session.add(p)
        db.session.flush()  # get p.id
        db.session.add(Inventory(product_id=p.id, quantity=stock))
        db.session.commit()
        return jsonify(product_to_dict(p, stock)), 201
    except Exception as e:
        db.session.rollback()
        logger.error("create_product failed: %s", e)
        return jsonify({"error": "database error"}), 500


@app.route("/products/<int:pid>", methods=["GET"])
def get_product(pid):
    try:
        p = Product.query.get(pid)
        if not p:
            return jsonify({"error": "not found"}), 404
        inv = Inventory.query.get(pid)
        return jsonify(product_to_dict(p, inv.quantity if inv else 0))
    except Exception as e:
        logger.error("get_product failed: %s", e)
        return jsonify({"error": "database error"}), 500


@app.route("/orders", methods=["POST"])
def create_order():
    """
    Payload:
      { "items": [ {"product_id": 1, "quantity": 2}, ... ],
        "discount_cents": 0 }

    Note: pricing is calculated from current product price_cents stored in DB.
    """
    data = request.get_json(silent=True) or {}
    items = data.get("items") or []
    try:
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({"error": "items required"}), 400

        discount_cents = int(data.get("discount_cents", 0))
        if discount_cents < 0:
            return jsonify({"error": "invalid discount"}), 400

        order = Order(status="CREATED")
        db.session.add(order)
        db.session.flush()

        subtotal = 0
        for it in items:
            pid = int(it.get("product_id"))
            qty = int(it.get("quantity"))
            if qty <= 0:
                raise ValueError("invalid quantity")

            p = Product.query.get(pid)
            if not p:
                return jsonify({"error": f"product {pid} not found"}), 404

            inv = Inventory.query.get(pid)
            if not inv or inv.quantity < qty:
                return jsonify({"error": f"insufficient stock for product {pid}"}), 409

            inv.quantity -= qty
            line_total = p.price_cents * qty
            subtotal += line_total
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=pid,
                    quantity=qty,
                    unit_price_cents=p.price_cents,
                    line_total_cents=line_total,
                )
            )

        total = max(0, subtotal - discount_cents)
        order.subtotal_cents = subtotal
        order.discount_cents = discount_cents
        order.total_cents = total
        db.session.commit()
        return jsonify(
            {
                "id": order.id,
                "status": order.status,
                "subtotal_cents": subtotal,
                "discount_cents": discount_cents,
                "total_cents": total,
            }
        ), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error("create_order failed: %s", e)
        return jsonify({"error": "database error"}), 500


@app.route("/orders/<int:oid>", methods=["GET"])
def get_order(oid):
    try:
        order = Order.query.get(oid)
        if not order:
            return jsonify({"error": "not found"}), 404
        items = OrderItem.query.filter_by(order_id=oid).order_by(OrderItem.id.asc()).all()
        return jsonify(
            {
                "id": order.id,
                "status": order.status,
                "subtotal_cents": order.subtotal_cents,
                "discount_cents": order.discount_cents,
                "total_cents": order.total_cents,
                "items": [
                    {
                        "product_id": i.product_id,
                        "quantity": i.quantity,
                        "unit_price_cents": i.unit_price_cents,
                        "line_total_cents": i.line_total_cents,
                    }
                    for i in items
                ],
            }
        )
    except Exception as e:
        logger.error("get_order failed: %s", e)
        return jsonify({"error": "database error"}), 500


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    try:
        username = (data.get("username") or "").strip()
        password = data.get("password", "")
        if not username or not password:
            return jsonify({"error": "username and password required"}), 400
        if len(username) < 3 or len(password) < 6:
            return jsonify({"error": "username must be at least 3 chars, password at least 6"}), 400

        if User.query.filter_by(username=username).first() is not None:
            return jsonify({"error": "username already exists"}), 409

        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"id": user.id, "username": user.username}), 201
    except Exception as e:
        db.session.rollback()
        logger.error("create_user failed: %s", e)
        return jsonify({"error": "database error"}), 500


@app.route("/users/login", methods=["POST"])
def login_user():
    data = request.get_json(silent=True) or {}
    try:
        username = (data.get("username") or "").strip()
        password = data.get("password", "")
        if not username or not password:
            return jsonify({"error": "username and password required"}), 400

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "invalid credentials"}), 401

        return jsonify({"id": user.id, "username": user.username}), 200
    except Exception as e:
        logger.error("login_user failed: %s", e)
        return jsonify({"error": "database error"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"}), 200

if __name__ == '__main__':
    # 监听 0.0.0.0 以便容器内外部均可访问
    app.run(host='0.0.0.0', port=PORT)
