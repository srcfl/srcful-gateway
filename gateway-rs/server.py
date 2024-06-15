from flask import Flask, request, jsonify
import subprocess
import os
import signal
import json

app = Flask(__name__)

# Get gateway settings path from the environment variable
settings_path = os.getenv('GATEWAY_SETTINGS')

# Global variable to store the process ID
gateway_process = None

@app.route('/start_gateway', methods=['POST'])
def start_gateway():
    global gateway_process
    try:
        # Start the helium_gateway with the specified config file
        gateway_process = subprocess.Popen(['./helium_gateway', '-c', settings_path, 'server'])
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
            return jsonify({"message": "helium_gateway stopped successfully"}), 200
        else:
            return jsonify({"error": "helium_gateway is not running"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_info', methods=['GET'])
def get_info():
    try:
        # Get info from the helium_gateway
        result = subprocess.run(['./helium_gateway', '-c', settings_path, 'key', 'info'], capture_output=True, text=True)
        # Parse the JSON string into a Python dictionary
        info_dict = json.loads(result.stdout)
        return jsonify(info_dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add_gateway', methods=['POST'])
def add_gateway():
    data = request.get_json()
    owner = data.get('owner')
    payer = data.get('payer')
    mode = data.get('mode')

    if not owner or not payer or not mode:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Run the helium_gateway add command with the provided arguments
        result = subprocess.run([
            './helium_gateway', '-c', settings_path, 'add',
            '--owner', owner,
            '--payer', payer,
            '--mode', mode
        ], capture_output=True, text=True)

        if result.returncode == 0:
            # Parse the JSON string into a Python dictionary
            info_dict = json.loads(result.stdout)
            return jsonify(info_dict), 200
        else:
            return jsonify({"error": "Command failed", "output": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_app():
   return app