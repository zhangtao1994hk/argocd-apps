import os
import logging
import requests
from flask import Flask, jsonify, redirect, Response, request

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s : %(message)s')
logger = logging.getLogger("frontend-service")

app = Flask(__name__)

# K3s Service DNS: 假设 Service 名字叫 backend-service
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:5000")

APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")

INDEX_HTML = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Mini Shop</title>
    <style>
      body { font-family: ui-sans-serif, system-ui, -apple-system; margin: 24px; max-width: 980px; }
      .row { display: flex; gap: 16px; flex-wrap: wrap; }
      .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; min-width: 280px; }
      h1 { margin: 0 0 12px; }
      table { border-collapse: collapse; width: 100%; }
      th, td { border-bottom: 1px solid #eee; padding: 8px; text-align: left; }
      input { padding: 6px 8px; width: 90px; }
      button { padding: 8px 12px; border-radius: 10px; border: 1px solid #111; background: #111; color: #fff; cursor: pointer; }
      button.secondary { background: #fff; color: #111; }
      .muted { color: #6b7280; font-size: 12px; }
      pre { background: #0b1020; color: #d1d5db; padding: 12px; border-radius: 12px; overflow: auto; }
    </style>
  </head>
  <body>
    <h1>Mini Shop <span class="muted" id="ver"></span></h1>
    <div class="row">
      <div class="card" style="flex: 2">
        <h3>Products</h3>
        <table id="products">
          <thead><tr><th>ID</th><th>SKU</th><th>Name</th><th>Price</th><th>Stock</th><th>Qty</th></tr></thead>
          <tbody></tbody>
        </table>
        <div style="margin-top: 12px; display: flex; gap: 12px; align-items: center;">
          <button onclick="createOrder()">Create order</button>
          <button class="secondary" onclick="loadProducts()">Refresh</button>
        </div>
      </div>
      <div class="card" style="flex: 1">
        <h3>Result</h3>
        <pre id="out">{}</pre>
        <div class="muted" style="margin-top:8px;">
          Tip: quantities >= 3 items will get 10% discount (backend rule).
        </div>
      </div>
    </div>
    <script>
      async function loadProducts() {
        const res = await fetch('/api/products');
        const data = await res.json();
        const tbody = document.querySelector('#products tbody');
        tbody.innerHTML = '';
        for (const p of data) {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${p.id}</td>
            <td>${p.sku}</td>
            <td>${p.name}</td>
            <td>${(p.price_cents/100).toFixed(2)}</td>
            <td>${p.stock ?? ''}</td>
            <td><input type="number" min="0" value="0" data-pid="${p.id}" /></td>
          `;
          tbody.appendChild(tr);
        }
      }

      async function createOrder() {
        const inputs = Array.from(document.querySelectorAll('input[data-pid]'));
        const items = inputs
          .map(i => ({ product_id: Number(i.dataset.pid), quantity: Number(i.value) }))
          .filter(x => x.quantity > 0);
        const res = await fetch('/api/orders', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ items })
        });
        const txt = await res.text();
        document.querySelector('#out').textContent = txt;
      }

      document.querySelector('#ver').textContent = '(' + (window.__APP_VERSION__ || 'unknown') + ')';
      loadProducts().catch(e => document.querySelector('#out').textContent = String(e));
    </script>
  </body>
</html>
"""


@app.route("/api/products", methods=["GET"])
def api_products():
    try:
        r = requests.get(f"{BACKEND_URL}/api/products", timeout=5)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error("Backend unreachable: %s", e)
        return jsonify({"error": "Gateway Error"}), 502


@app.route("/api/orders", methods=["POST"])
def api_orders():
    try:
        r = requests.post(f"{BACKEND_URL}/api/orders", json=(request.get_json(silent=True) or {}), timeout=8)
        return Response(r.content, status=r.status_code, content_type=r.headers.get("Content-Type", "application/json"))
    except Exception as e:
        logger.error("Backend unreachable: %s", e)
        return jsonify({"error": "Gateway Error"}), 502

@app.route('/welcome', methods=['GET'])
def welcome():
    logger.info("Frontend: Welcome endpoint called")
    return jsonify({
        "message": "Welcome to the Frontend Service!",
        "version": APP_VERSION,
        "status": "ok"
    }), 200

@app.route('/error-test')
def error_test():
    raise Exception("Intentional 503 error for canary testing")

@app.route('/', methods=['GET'])
def index():
    html = INDEX_HTML.replace("window.__APP_VERSION__ || 'unknown'", f"'{APP_VERSION}'")
    return Response(html, content_type="text/html; charset=utf-8")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


