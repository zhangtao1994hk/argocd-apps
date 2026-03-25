import os
import logging
import requests
from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s : %(message)s')
logger = logging.getLogger("backend-service")

app = Flask(__name__)

# K3s Service DNS: 假设你在 K8s 里 Service 名字叫 dao-service
DAO_URL = os.getenv("DAO_URL", "http://dao-service:5000")

@app.route('/product/<int:pid>', methods=['GET'])
def get_product(pid):
    logger.info(f"Backend processing request for product {pid}")
    
    try:
        # 调用 DAO 服务
        response = requests.get(f"{DAO_URL}/product/{pid}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            # 这里可以添加一些业务逻辑，比如价格打折
            data['price'] = round(data['price'] * 0.9, 2)
            logger.info(f"Backend retrieved and processed product {pid}")
            return jsonify(data)
        else:
            logger.warning(f"DAO returned {response.status_code} for product {pid}")
            return jsonify({"error": "Product not found in DAO"}), response.status_code
            
    except requests.exceptions.RequestException as e:
        logger.error(f"DAO Service Unavailable: {str(e)}")
        return jsonify({"error": "Service Unavailable"}), 503

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
