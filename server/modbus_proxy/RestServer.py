import signal

from flask import Flask, request, jsonify

from ThreadedServer import ThreadedServer

proxy_server = None

app = Flask(__name__)


@app.route('/api/proxy/start', methods=['POST'])
def start_proxy():
    global proxy_server
    if proxy_server is None or not proxy_server.is_alive():
        listen_host = request.json.get('listen_host', '0.0.0.0')
        listen_port = request.json.get('listen_port', 5020)
        target_host = request.json.get('target_host')
        target_port = request.json.get('target_port')
        
        if not target_host or not target_port:
            return jsonify({"error": "target_host and target_port are required"}), 400

        proxy_server = ThreadedServer(listen_host, listen_port, target_host, int(target_port))
        proxy_server.start()
        return jsonify({"status": "Proxy started"}), 200
    else:
        return jsonify({"status": "Proxy already running"}), 200


@app.route('/api/proxy/stop', methods=['POST'])
def stop_proxy():
    global proxy_server
    if proxy_server is not None:
        proxy_server.shutdown()
        proxy_server.join()
        proxy_server = None
        return jsonify({"status": "Proxy stopped"}), 200
    else:
        return jsonify({"status": "Proxy not running"}), 200


@app.route('/api/proxy/status', methods=['GET'])
def status():
    global proxy_server
    if proxy_server is not None and proxy_server.is_alive():
        return jsonify({"status": "Proxy is running"}), 200
    else:
        return jsonify({"status": "Proxy is not running"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    if proxy_server is not None:
        proxy_server.shutdown()