import os
import logging
import requests
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s : %(message)s')

logger = logging.getLogger("backend-service")

app = Flask(__name__)

DAO_URL = os.getenv("DAO_URL", "http://dao-service:5000")

def compute_discount_cents(items, products_by_id):
    """
    简单业务规则示例：
    - 单笔订单总件数 >= 3，整单打 10% 折扣（向下取整到分）
    """
    total_qty = sum(int(i.get("quantity", 0)) for i in items)
    if total_qty < 3:
        return 0
    subtotal = 0
    for i in items:
        pid = int(i["product_id"])
        qty = int(i["quantity"])
        subtotal += products_by_id[pid]["price_cents"] * qty
    return int(subtotal * 0.10)


@app.route("/api/products", methods=["GET"])
def list_products():
    try:
        r = requests.get(f"{DAO_URL}/products", timeout=5)
        return (r.content, r.status_code, {"Content-Type": r.headers.get("Content-Type", "application/json")})
    except requests.exceptions.RequestException as e:
        logger.error("DAO unavailable: %s", e)
        return jsonify({"error": "Service Unavailable"}), 503


@app.route("/api/products/<int:pid>", methods=["GET"])
def get_product(pid):
    try:
        r = requests.get(f"{DAO_URL}/products/{pid}", timeout=5)
        return (r.content, r.status_code, {"Content-Type": r.headers.get("Content-Type", "application/json")})
    except requests.exceptions.RequestException as e:
        logger.error("DAO unavailable: %s", e)
        return jsonify({"error": "Service Unavailable"}), 503


@app.route("/api/orders", methods=["POST"])
def create_order():
    payload = request.get_json(silent=True) or {}
    items = payload.get("items") or []
    if not isinstance(items, list) or len(items) == 0:
        return jsonify({"error": "items required"}), 400

    # 拉取商品信息用于计算折扣（只做最小实现，不做缓存）
    try:
        r = requests.get(f"{DAO_URL}/products", timeout=5)
        if r.status_code != 200:
            return jsonify({"error": "failed to load products"}), 502
        products = r.json()
    except requests.exceptions.RequestException as e:
        logger.error("DAO unavailable: %s", e)
        return jsonify({"error": "Service Unavailable"}), 503

    products_by_id = {p["id"]: p for p in products}
    for i in items:
        try:
            pid = int(i.get("product_id"))
            qty = int(i.get("quantity"))
        except Exception:
            return jsonify({"error": "invalid items"}), 400
        if pid not in products_by_id or qty <= 0:
            return jsonify({"error": "invalid items"}), 400

    discount_cents = compute_discount_cents(items, products_by_id)

    try:
        r2 = requests.post(
            f"{DAO_URL}/orders",
            json={"items": items, "discount_cents": discount_cents},
            timeout=8,
        )
        return (r2.content, r2.status_code, {"Content-Type": r2.headers.get("Content-Type", "application/json")})
    except requests.exceptions.RequestException as e:
        logger.error("DAO unavailable: %s", e)
        return jsonify({"error": "Service Unavailable"}), 503

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
