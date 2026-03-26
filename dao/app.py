import os
import logging
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy



logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s : %(message)s')
logger = logging.getLogger("dao-service")

app = Flask(__name__)

# 2. 数据库配置
# 生产环境建议通过环境变量注入，这里提供默认值
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "777777")
DB_HOST = os.getenv("DB_HOST", "10.128.0.2") 
DB_NAME = os.getenv("DB_NAME", "app_db")
PORT = int(os.getenv("PORT", 5000)) # 从环境变量读取端口，默认5000

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 3. 定义数据模型
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)

# 初始化表
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize DB: {e}")

# 4. API 接口
@app.route('/product', methods=['POST'])
def add_product():
    data = request.json
    try:
        new_product = Product(name=data['name'], price=data['price'])
        db.session.add(new_product)
        db.session.commit()
        logger.info(f"Inserted new product: {new_product.name}")
        return jsonify({"message": "Success", "id": new_product.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to insert product: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/product/<int:pid>', methods=['GET'])
def get_product(pid):
    try:
        product = Product.query.get(pid)
        if product:
            logger.info(f"Query found product: {product.name}")
            return jsonify({"id": product.id, "name": product.name, "price": product.price})
        else:
            logger.warning(f"Product {pid} not found")
            return jsonify({"error": "Not Found"}), 404
    except Exception as e:
        logger.error(f"Database query error: {str(e)}")
        return jsonify({"error": "Database error"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"}), 200

if __name__ == '__main__':
    # 监听 0.0.0.0 以便容器内外部均可访问
    app.run(host='0.0.0.0', port=PORT)
