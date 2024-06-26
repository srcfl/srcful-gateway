from flask import Flask, request, jsonify
import subprocess
import os
import signal
import json
import logging
from client import GatewayClient
from protos import add_gateway_pb2
import base58 

logging.basicConfig(level=logging.INFO)
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
    global gateway
    try:
        # Start the helium_gateway with the specified config file
        gateway_process = subprocess.Popen(['./helium_gateway', '-c', settings_path, 'server'])
        gateway = GatewayClient()
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
    global gateway
    try:
        # Get info from the helium_gateway
        result = subprocess.run(['./helium_gateway', '-c', settings_path, 'key', 'info'], capture_output=True, text=True)
        # Parse the JSON string into a Python dictionary
        info_dict = json.loads(result.stdout)
        logger.info(f"Gateway info: {info_dict}")
        return jsonify(info_dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_gateway', methods=['POST'])
def add_gateway():
    global gateway

    data = request.data
    
    logger.info(f"Request data: {data}")

    add_gw_details = add_gateway_pb2.add_gateway_v1()
    add_gw_details.ParseFromString(bytes(data))

    logger.info(f"add gateway owner {add_gw_details.owner}, fee {add_gw_details.fee} "
                         f"amount {add_gw_details.amount}, payer {add_gw_details.payer}")

    try:
        txn = gateway.create_add_gateway_txn(
            owner_address=add_gw_details.owner,
            payer_address='14h2zf1gEr9NmvDb2U53qucLN2jLrKU1ECBoxGnSnQ6tiT6V2kM'
        )
        
        return jsonify({"txn": base58.b58encode(txn).decode('utf-8')}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def create_app():
    global gateway_process
    global gateway

    # Start the helium_gateway with the specified config file
    gateway_process = subprocess.Popen(['./helium_gateway', '-c', settings_path, 'server'])
    gateway = GatewayClient()
    logger.info(f"helium_gateway started with PID: {gateway_process.pid}")
    return app