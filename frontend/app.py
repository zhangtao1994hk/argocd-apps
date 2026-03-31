import os
import logging
import requests
from flask import Flask, jsonify, redirect 

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s : %(message)s')
logger = logging.getLogger("frontend-service")

app = Flask(__name__)

# K3s Service DNS: 假设 Service 名字叫 backend-service
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:5000")


APP_VERSION = os.getenv("APP_VERSION", "v1.0.0")

@app.route('/api/view/<int:pid>', methods=['GET'])
def view_product(pid):
    logger.info(f"Frontend: User request for product {pid}")
    
    try:
        response = requests.get(f"{BACKEND_URL}/product/{pid}", timeout=5)
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": "Backend Error"}), response.status_code
            
    except Exception as e:
        logger.error(f"Frontend: Critical failure, backend unreachable: {str(e)}")
        return jsonify({"error": "Gateway Error"}), 502

@app.route('/welcome', methods=['GET'])
def welcome():
    logger.info("Frontend: Welcome endpoint called")
    return jsonify({
        "message": "Welcome to the Frontend Service!",
        "version": APP_VERSION,
        "status": "ok"
    }), 503

@app.route('/', methods=['GET'])
def index():
    return redirect('/api/view/1', code=302)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "UP"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


