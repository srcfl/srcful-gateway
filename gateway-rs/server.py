from flask import Flask, request, jsonify
import subprocess
import os
import signal
import json
import logging
from client import GatewayClient
import base58 

# change the logging level to debug from root level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(name=__name__)

app = Flask(__name__)

# Get gateway settings path from the environment variable
settings_path = os.getenv('GATEWAY_SETTINGS')

# Global variable to store the process ID
gateway_process = None

gateway = None

@app.route('/start_gateway', methods=['POST'])
def start_gateway():
    global gateway_process
    try:
        # Start the helium_gateway with the specified config file
        gateway_process = subprocess.Popen(['./helium_gateway', '-c', settings_path, 'server'])
        logger.info(f"helium_gateway started with PID: {gateway_process.pid}")
        return jsonify({"message": "helium_gateway started successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stop_gateway', methods=['POST'])
def stop_gateway():
    global gateway_process
    try:
        if gateway_process:
            # Terminate the helium_gateway process
            os.kill(gateway_process.pid, signal.SIGTERM)
            gateway_process = None
            logger.info("helium_gateway stopped")
            return jsonify({"message": "helium_gateway stopped successfully"}), 200
        else:
            logger.warning("helium_gateway is not running")
            return jsonify({"error": "helium_gateway is not running"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/onboading_keys', methods=['GET'])
def get_info():
    try:
        # Get info from the helium_gateway
        result = subprocess.run(['./helium_gateway', '-c', settings_path, 'info', 'key'], capture_output=True, text=True)
        # Parse the JSON string into a Python dictionary
        info_dict = json.loads(result.stdout)
        logger.info(f"Gateway info: {info_dict}")
        return jsonify(info_dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/region', methods=['GET'])
def get_region():
    try:
        # Get info from the helium_gateway
        result = subprocess.run(['./helium_gateway', '-c', settings_path, 'info', 'region'], capture_output=True, text=True)
        # Parse the JSON string into a Python dictionary
        info_dict = json.loads(result.stdout)
        logger.info(f"Gateway info: {info_dict}")
        return jsonify(info_dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/add_gateway', methods=['POST'])
def add_gateway():
    
    data = request.get_json()
    data = json.loads(data)
    logger.info(f"Request data: {type(data)}")
    logger.info(f"Request data: {data}")
    owner = data.get('owner')
    payer = data.get('payer')
    logger.info(f"add gateway owner {owner} payer {payer}")
    
    result = subprocess.run([
            './helium_gateway', '-c', settings_path, 'add',
            '--owner', owner,
            '--payer', payer,
            '--mode', 'full'
        ], capture_output=True, text=True)

    try:
        
        json_payload = json.loads(result.stdout)
        logger.info(f"Json payload {json_payload}")
        
        # log address, mode, owner, payer and txn 
        logger.info(f"Address: {json_payload['address']}")
        logger.info(f"Mode: {json_payload['mode']}")
        logger.info(f"Owner: {json_payload['owner']}")
        logger.info(f"Payer: {json_payload['payer']}")
        logger.info(f"Txn: {json_payload['txn']}")
        
        txn = json_payload['txn']
            
        logger.info(f"Transaction created: {txn}")
        return jsonify({"txn": txn}), 200
    
    except Exception as e:
        logger.error(f"Error adding gateway: {str(e)}")
        return jsonify({"error": str(e)}), 500


def create_app():
    global gateway_process
    
    # Start the helium_gateway with the specified config file
    gateway_process = subprocess.Popen(['./helium_gateway', '-c', settings_path, 'server'])
    gateway = GatewayClient()
    logger.info(f"helium_gateway started with PID: {gateway_process.pid}")
    return app