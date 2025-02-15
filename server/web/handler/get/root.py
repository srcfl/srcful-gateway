import server.crypto.crypto as crypto

from ..handler import GetHandler
from ..requestData import RequestData


class Handler(GetHandler):
    def do_get(self, data: RequestData):
        ret = """
        <html>
        <head>
            <title>Srcful Energy Gateway</title>
            <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIxIiBoZWlnaHQ9IjEyMCIgdmlld0JveD0iMCAwIDEyMSAxMjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iNjAuMjcxIiBjeT0iNjAiIHI9IjYwIiBmaWxsPSIjMkIyQjJCIi8+PHBhdGggZD0iTTM2LjA5NzMgNTguNTIyNUw2NC4xMDU5IDI0LjUyNjlDNjYuMTA2OCAyMi4wOTg0IDcwLjAyMDkgMjMuOTkyMiA2OS4zNTg0IDI3LjA2ODNMNjMuODczOCA1Mi41MzQ3QzYzLjQ1MiA1NC40OTMxIDY1LjAzIDU2LjMwNzUgNjcuMDI4MSA1Ni4xNjEzTDgxLjE5NDUgNTUuMTI0N0M4My44ODkgNTQuOTI3NiA4NS40NTI2IDU4LjExMTQgODMuNjQ5NCA2MC4xMjMyTDUyLjIwODkgOTUuMjAwOUM1MC4wNjY0IDk3LjU5MTIgNDYuMTcyMyA5NS40MDQ0IDQ3LjA5ODIgOTIuMzMwOUw1NS4zNzU0IDY0Ljg1NDNDNTYuMDIyMiA2Mi43MDc1IDU0LjE3MyA2MC42MzQ5IDUxLjk2NjYgNjEuMDMzN0wzOC45NDg1IDYzLjM4NjNDMzYuMTk3IDYzLjg4MzYgMzQuMzE5MyA2MC42ODA1IDM2LjA5NzMgNTguNTIyNVoiIGZpbGw9IiMwMEZGODQiLz48L3N2Zz4=">
            <style>
                body {
                    font-family: system-ui, -apple-system, sans-serif;
                    background: linear-gradient(135deg, #2B2B2B 0%, #1a1a1a 100%);
                    color: #fff;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 15px;
                }
                .container {
                    background: rgba(255, 255, 255, 0.03);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(0, 255, 133, 0.1);
                    border-radius: 12px;
                    padding: 25px;
                    width: 90%;
                    max-width: 1200px;
                }
                .header {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    margin-bottom: 25px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid rgba(0, 255, 133, 0.2);
                }
                .logo {
                    width: 40px;
                    height: 40px;
                }
                h1, h2, h3 {
                    color: #00FF85;
                    margin: 0;
                    font-weight: 500;
                }
                h1 {
                    font-size: 24px;
                }
                h2 {
                    font-size: 18px;
                    margin-top: 25px;
                    margin-bottom: 15px;
                }
                h3 {
                    font-size: 16px;
                    margin-top: 15px;
                    margin-bottom: 10px;
                    opacity: 0.9;
                }
                .section {
                    margin: 15px 0;
                }
                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 10px;
                }
                .card {
                    background: rgba(0, 255, 133, 0.05);
                    border-radius: 8px;
                    padding: 12px;
                }
                .card-header {
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    opacity: 0.7;
                    margin-bottom: 4px;
                }
                .card-value {
                    color: #00FF85;
                    font-size: 14px;
                    font-family: monospace;
                    word-break: break-all;
                }
                .messages {
                    margin-top: 15px;
                }
                .message {
                    padding: 8px 12px;
                    margin: 5px 0;
                    border-radius: 6px;
                    font-size: 13px;
                }
                .message.error { background: rgba(255, 59, 48, 0.1); border-left: 2px solid #ff3b30; }
                .message.warning { background: rgba(255, 204, 0, 0.1); border-left: 2px solid #ffcc00; }
                .message.info { background: rgba(0, 255, 133, 0.1); border-left: 2px solid #00FF85; }
                .device-card {
                    background: rgba(0, 255, 133, 0.05);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 10px;
                }
                .device-details {
                    margin-top: 8px;
                    padding-left: 12px;
                    border-left: 1px solid rgba(0, 255, 133, 0.2);
                    font-size: 13px;
                }
                .device-property {
                    margin: 4px 0;
                    display: flex;
                    align-items: baseline;
                }
                .device-property-label {
                    color: rgba(255, 255, 255, 0.7);
                    width: 60px;
                }
                .device-property-value {
                    color: #00FF85;
                    margin-left: 8px;
                    font-family: monospace;
                }
                .device-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 12px;
                }
                .device-card {
                    background: rgba(0, 255, 133, 0.05);
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 13px;
                }
                .device-card .card-header {
                    font-size: 13px;
                    text-transform: none;
                    letter-spacing: 0;
                    opacity: 0.85;
                    margin-bottom: 8px;
                    color: #00FF85;
                }
                .device-details {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }
                .device-property {
                    margin: 0;
                    display: flex;
                    align-items: baseline;
                    font-family: monospace;
                    font-size: 12px;
                }
                .device-property-label {
                    color: rgba(255, 255, 255, 0.7);
                    min-width: 60px;
                }
                .device-property-value {
                    color: #00FF85;
                }
                .network-info {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 10px;
                }
                .app-links {
                    background: rgba(0, 255, 133, 0.05);
                    border-radius: 8px;
                    padding: 12px 15px;
                    margin: 20px 0;
                    font-size: 14px;
                }
                .app-links-header {
                    color: rgba(255, 255, 255, 0.7);
                    margin-bottom: 8px;
                    text-align: center;
                }
                .app-links-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 10px;
                    text-align: center;
                }
                .app-link {
                    padding: 8px;
                    border-radius: 6px;
                    background: rgba(0, 255, 133, 0.03);
                    transition: background-color 0.2s;
                }
                .app-link:hover {
                    background: rgba(0, 255, 133, 0.08);
                }
                .app-link a {
                    color: #00FF85;
                    text-decoration: none;
                    font-weight: 500;
                }
                .app-link a:hover {
                    text-decoration: underline;
                }
                @media (max-width: 768px) {
                    .container {
                        padding: 15px;
                    }
                    .grid {
                        grid-template-columns: 1fr;
                    }
                    .app-links-grid {
                        grid-template-columns: 1fr;
                    }
                    .device-grid {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <svg width="40" height="40" viewBox="0 0 121 120" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo">
                        <circle cx="60.271" cy="60" r="60" fill="#2B2B2B"/>
                        <path d="M36.0973 58.5225L64.1059 24.5269C66.1068 22.0984 70.0209 23.9922 69.3584 27.0683L63.8738 52.5347C63.452 54.4931 65.03 56.3075 67.0281 56.1613L81.1945 55.1247C83.889 54.9276 85.4526 58.1114 83.6494 60.1232L52.2089 95.2009C50.0664 97.5912 46.1723 95.4044 47.0982 92.3309L55.3754 64.8543C56.0222 62.7075 54.173 60.6349 51.9666 61.0337L38.9485 63.3863C36.197 63.8836 34.3193 60.6805 36.0973 58.5225Z" fill="#00FF84"/>
                    </svg>
                    <h1>Sourceful Energy Gateway</h1>
                </div>
                
                <div class="app-links">
                    <div class="app-links-header">For configuration, please use our app:</div>
                    <div class="app-links-grid">
                        <div class="app-link">
                            <a href="https://play.google.com/store/apps/details?id=com.sourceful_labs.energy" target="_blank">Play Store</a>
                        </div>
                        <div class="app-link">
                            <a href="https://apps.apple.com/se/app/sourceful-energy/id6736659172" target="_blank">App Store</a>
                        </div>
                        <div class="app-link">
                            <a href="https://app.srcful.io/" target="_blank">Web App</a>
                        </div>
                    </div>
                </div>
        """

        # Get the full state
        state = data.bb.state

        # Status Section
        ret += '<div class="section">'
        ret += '<h2>Status</h2>'
        ret += '<div class="grid">'

        # Version and Uptime cards
        uptime = state['status']['uptime']
        days, remainder = divmod(uptime // 1000, 60 * 60 * 24)
        hours, remainder = divmod(remainder, 60 * 60)
        minutes, seconds = divmod(remainder, 60)

        ret += f'''
            <div class="card">
                <div class="card-header">Version</div>
                <div class="card-value">{state['status']['version']}</div>
            </div>
            <div class="card">
                <div class="card-header">Uptime</div>
                <div class="card-value">{int(days):02d} days {int(hours):02d} hours {int(minutes):02d} minutes {int(seconds):02d} seconds</div>
            </div>
        '''
        ret += '</div></div>'

        # Devices Section
        ret += '<div class="section">'
        ret += '<h2>Devices</h2>'

        # Saved Devices
        if state['devices']['saved']:
            ret += '<h3>Saved Devices</h3>'
            ret += '<div class="device-grid">'
            for device in state['devices']['saved']:
                ret += f'''
                    <div class="device-card">
                        <div class="card-header">{device['name']}</div>
                        <div class="device-details">
                            <div class="device-property">
                                <span class="device-property-label">ID:</span>
                                <span class="device-property-value">{device['id']}</span>
                            </div>
                            <div class="device-property">
                                <span class="device-property-label">Status:</span>
                                <span class="device-property-value">{'Connected' if device['is_open'] else 'Disconnected'}</span>
                            </div>
                            <div class="device-property">
                                <span class="device-property-label">Type:</span>
                                <span class="device-property-value">{device['connection']['device_type']}</span>
                            </div>
                            <div class="device-property">
                                <span class="device-property-label">IP:</span>
                                <span class="device-property-value">{device['connection']['ip']}:{device['connection']['port']}</span>
                            </div>
                            <div class="device-property">
                                <span class="device-property-label">MAC:</span>
                                <span class="device-property-value">{device['connection']['mac']}</span>
                            </div>
                        </div>
                    </div>
                '''
            ret += '</div>'
        ret += '</div>'

        # Crypto Section
        ret += '<div class="section">'
        ret += '<h2>Crypto</h2>'
        ret += '<div class="grid">'
        for key, value in state['crypto'].items():
            formatted_key = ' '.join(word.capitalize() for word in key.split('_'))
            ret += f'''
                <div class="card">
                    <div class="card-header">{formatted_key}</div>
                    <div class="card-value">{value}</div>
                </div>
            '''
        ret += '</div></div>'

        # Network Section
        ret += '<div class="section">'
        ret += '<h2>Network</h2>'

        network = state['network']
        if 'error' in network:
            ret += f'''
                <div class="card">
                    <div class="card-header">Error</div>
                    <div class="card-value">{network['error']}</div>
                </div>
            '''
        else:
            if 'wifi' in network:
                wifi = network['wifi']
                ret += '<h3>WiFi</h3>'
                ret += '<div class="network-info">'
                ret += f'''
                    <div class="card">
                        <div class="card-header">Connected SSID</div>
                        <div class="card-value">{wifi.get('connected', 'Not connected')}</div>
                    </div>
                '''
                if wifi.get('ssids'):
                    ret += '''
                        <div class="card">
                            <div class="card-header">Available Networks</div>
                            <div class="card-value">
                    '''
                    ret += '<br>'.join(wifi['ssids'])
                    ret += '</div></div>'
                ret += '</div>'

            if 'address' in network:
                addr = network['address']
                ret += '<h3>Network Addresses</h3>'
                ret += '<div class="network-info">'
                for key in ['ip', 'port', 'eth0_mac', 'wlan0_mac']:
                    if key in addr:
                        ret += f'''
                            <div class="card">
                                <div class="card-header">{key.replace('_', ' ').upper()}</div>
                                <div class="card-value">{addr[key]}</div>
                            </div>
                        '''
                ret += '</div>'

                if 'interfaces' in addr:
                    ret += '<h3>Network Interfaces</h3>'
                    ret += '<div class="network-info">'
                    for interface, ip in addr['interfaces'].items():
                        ret += f'''
                            <div class="card">
                                <div class="card-header">{interface}</div>
                                <div class="card-value">{ip}</div>
                            </div>
                        '''
                    ret += '</div>'
        ret += '</div>'

        # Messages Section
        if state['status']['messages']:
            ret += '<div class="section">'
            ret += '<h2>Messages</h2>'
            ret += '<div class="messages">'
            for msg in state['status']['messages']:
                message_text = msg['message'][0] % tuple(msg['message'][1:]) if isinstance(msg['message'], list) else msg['message']
                ret += f'''
                    <div class="message {msg['type']}">
                        {message_text}
                    </div>
                '''
            ret += '</div></div>'

        ret += "</div></body></html>"
        return 200, ret
