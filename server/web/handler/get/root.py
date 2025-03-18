import server.crypto.crypto as crypto

from ..handler import GetHandler
from ..requestData import RequestData


class Handler(GetHandler):
    def do_get(self, data: RequestData):
        # Fetch the gateway name
        from server.tasks.getNameTask import GetNameTask
        from server.network.network_utils import NetworkUtils

        # Get the gateway name
        name_task = GetNameTask(0, data.bb)
        name_task.execute(0)

        # Default name if not available
        gateway_name = "Sourceful Energy Gateway"

        # Get hostname of the current gateway
        hostname = ""
        try:
            # Try to get the hostname from the network interface
            import socket
            hostname = socket.gethostname()
            # If the hostname is too long or complex, simplify it
            if '.' in hostname:
                hostname = hostname.split('.')[0]
        except Exception:
            # Fallback to a simple identifier if hostname can't be retrieved
            hostname = "gateway"

        # Update with actual name if available
        if hasattr(name_task, 'name') and name_task.name is not None:
            gateway_name = name_task.name

        ret = """
        <html>
        <head>
            <title>Sourceful Energy Gateway</title>
            <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIxIiBoZWlnaHQ9IjEyMCIgdmlld0JveD0iMCAwIDEyMSAxMjAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iNjAuMjcxIiBjeT0iNjAiIHI9IjYwIiBmaWxsPSIjMkIyQjJCIi8+PHBhdGggZD0iTTM2LjA5NzMgNTguNTIyNUw2NC4xMDU5IDI0LjUyNjlDNjYuMTA2OCAyMi4wOTg0IDcwLjAyMDkgMjMuOTkyMiA2OS4zNTg0IDI3LjA2ODNMNjMuODczOCA1Mi41MzQ3QzYzLjQ1MiA1NC40OTMxIDY1LjAzIDU2LjMwNzUgNjcuMDI4MSA1Ni4xNjEzTDgxLjE5NDUgNTUuMTI0N0M4My44ODkgNTQuOTI3NiA4NS40NTI2IDU4LjExMTQgODMuNjQ5NCA2MC4xMjMyTDUyLjIwODkgOTUuMjAwOUM1MC4wNjY0IDk3LjU5MTIgNDYuMTcyMyA5NS40MDQ0IDQ3LjA5ODIgOTIuMzMwOUw1NS4zNzU0IDY0Ljg1NDNDNTYuMDIyMiA2Mi43MDc1IDU0LjE3MyA2MC42MzQ5IDUxLjk2NjYgNjEuMDMzN0wzOC45NDg1IDYzLjM4NjNDMzYuMTk3IDYzLjg4MzYgMzQuMzE5MyA2MC42ODA1IDM2LjA5NzMgNTguNTIyNVoiIGZpbGw9IiMwMEZGODQiLz48L3N2Zz4=">
            <!-- Import fonts -->
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>
                /* Premium design variables */
                :root {
                    --primary: #00d672;
                    --primary-gradient: linear-gradient(135deg, #00d672 0%, #00b561 100%);
                    --primary-dark: #00a759;
                    --primary-glow: rgba(0, 214, 114, 0.15);
                    --background: #1a1a1a;
                    --background-dark: #121212;
                    --card-bg: rgba(255, 255, 255, 0.03);
                    --card-hover: rgba(255, 255, 255, 0.05);
                    --text: #f5f5f5;
                    --text-secondary: rgba(255, 255, 255, 0.7);
                    --border: rgba(255, 255, 255, 0.08);
                    --border-hover: rgba(0, 214, 114, 0.3);
                    --shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
                    --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.15);
                }
                
                html {
                    font-size: 95%;
                    box-sizing: border-box;
                }
                
                *, *:before, *:after {
                    box-sizing: inherit;
                    margin: 0;
                    padding: 0;
                }
                
                body {
                    font-family: 'Inter', system-ui, -apple-system, sans-serif;
                    background: linear-gradient(135deg, var(--background) 0%, var(--background-dark) 100%);
                    color: var(--text);
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 1rem;
                    line-height: 1.6;
                    background-attachment: fixed;
                }
                
                .container {
                    background: rgba(26, 26, 26, 0.85);
                    backdrop-filter: blur(15px);
                    -webkit-backdrop-filter: blur(15px);
                    border: 1px solid var(--border);
                    border-radius: 1.25rem;
                    padding: 2rem;
                    width: 95%;
                    max-width: 1200px;
                    box-shadow: var(--shadow);
                    position: relative;
                    overflow: hidden;
                }
                
                /* Subtle background glow effect */
                .container::before {
                    content: "";
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(
                        circle at center,
                        var(--primary-glow) 0%,
                        transparent 70%
                    );
                    opacity: 0.05;
                    z-index: -1;
                }
                
                .header {
                    display: flex;
                    align-items: center;
                    gap: 1.25rem;
                    margin-bottom: 2rem;
                    padding-bottom: 1.25rem;
                    border-bottom: 1px solid var(--border);
                    position: relative;
                }
                
                .logo {
                    width: 3.5rem;
                    height: 3.5rem;
                    filter: drop-shadow(0 4px 10px rgba(0, 214, 114, 0.35));
                }
                
                h1, h2, h3 {
                    color: var(--text);
                    margin: 0;
                    font-weight: 600;
                    letter-spacing: -0.02em;
                }
                
                h1 {
                    font-size: 1.9rem;
                    background: var(--primary-gradient);
                    -webkit-background-clip: text;
                    background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                
                h2 {
                    font-size: 1.4rem;
                    margin-top: 1.75rem;
                    margin-bottom: 1.1rem;
                    display: flex;
                    align-items: center;
                    color: var(--text);
                }
                
                h2::before {
                    content: "";
                    display: inline-block;
                    width: 0.9rem;
                    height: 0.2rem;
                    background: var(--primary-gradient);
                    margin-right: 0.75rem;
                    border-radius: 1rem;
                }
                
                h2::after {
                    content: "";
                    height: 1px;
                    flex-grow: 1;
                    background: linear-gradient(90deg, var(--border) 0%, transparent 100%);
                    margin-left: 0.75rem;
                }
                
                h3 {
                    font-size: 1.1rem;
                    margin-top: 1.25rem;
                    margin-bottom: 0.9rem;
                    color: var(--text-secondary);
                }
                
                .section {
                    margin: 1.75rem 0;
                    position: relative;
                }
                
                .grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr));
                    gap: 1.1rem;
                }
                
                article {
                    background: var(--card-bg);
                    border-radius: 1rem;
                    padding: 1.25rem;
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                    border: 1px solid var(--border);
                    box-shadow: var(--shadow-sm);
                    position: relative;
                    overflow: hidden;
                }
                
                article:hover {
                    transform: translateY(-3px);
                    border-color: var(--border-hover);
                    background: var(--card-hover);
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
                }
                
                /* Glow effect on hover */
                article::after {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 0;
                    background: linear-gradient(to bottom, var(--primary-glow), transparent);
                    opacity: 0;
                    transition: all 0.3s ease;
                }
                
                article:hover::after {
                    height: 4px;
                    opacity: 1;
                }
                
                .card-header {
                    font-size: 0.9rem;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    color: var(--text-secondary);
                    margin-bottom: 0.7rem;
                    font-weight: 500;
                }
                
                .card-value {
                    color: var(--primary);
                    font-size: 1.05rem;
                    font-family: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
                    word-break: break-all;
                    font-weight: 500;
                }
                
                .messages {
                    margin-top: 1.1rem;
                    display: flex;
                    flex-direction: column;
                    gap: 0.9rem;
                }
                
                .message {
                    padding: 1.1rem;
                    border-radius: 0.75rem;
                    font-size: 1rem;
                    transition: transform 0.3s ease;
                    box-shadow: var(--shadow-sm);
                }
                
                .message:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
                }
                
                .message.error { 
                    background: rgba(255, 59, 48, 0.1); 
                    border-left: 4px solid #ff3b30; 
                }
                
                .message.warning { 
                    background: rgba(255, 204, 0, 0.1); 
                    border-left: 4px solid #ffcc00; 
                }
                
                .message.info { 
                    background: rgba(0, 214, 114, 0.08); 
                    border-left: 4px solid var(--primary); 
                }
                
                .device-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
                    gap: 1.1rem;
                }
                
                .device-card {
                    background: var(--card-bg);
                    border-radius: 1rem;
                    padding: 1.25rem;
                    margin-bottom: 0.6rem;
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                    border: 1px solid var(--border);
                    box-shadow: var(--shadow-sm);
                    position: relative;
                    overflow: hidden;
                }
                
                .device-card:hover {
                    transform: translateY(-3px);
                    border-color: var(--border-hover);
                    background: var(--card-hover);
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
                }
                
                /* Device card hover effect */
                .device-card::after {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 0;
                    background: linear-gradient(to bottom, var(--primary-glow), transparent);
                    opacity: 0;
                    transition: all 0.3s ease;
                }
                
                .device-card:hover::after {
                    height: 4px;
                    opacity: 1;
                }
                
                .device-card .card-header {
                    font-size: 1.15rem;
                    text-transform: none;
                    letter-spacing: -0.01em;
                    margin-bottom: 0.8rem;
                    color: var(--primary);
                    font-weight: 600;
                }
                
                .device-details {
                    margin-top: 0.8rem;
                    padding-left: 1rem;
                    border-left: 2px solid var(--border);
                    transition: all 0.3s ease;
                }
                
                .device-card:hover .device-details {
                    border-left-color: var(--primary); 
                }
                
                .device-property {
                    margin: 0.5rem 0;
                    display: flex;
                    align-items: baseline;
                }
                
                .device-property-label {
                    color: var(--text-secondary);
                    min-width: 4rem;
                    font-size: 0.9rem;
                    font-weight: 500;
                }
                
                .device-property-value {
                    color: var(--text);
                    margin-left: 0.6rem;
                    font-family: monospace;
                    font-size: 0.9rem;
                    font-weight: 500;
                }
                
                .network-info {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr));
                    gap: 1.1rem;
                }
                
                .app-links {
                    background: linear-gradient(135deg, rgba(26, 26, 26, 0.8) 0%, rgba(22, 22, 22, 0.9) 100%);
                    border-radius: 1rem;
                    padding: 1.75rem;
                    margin: 2.25rem 0;
                    border: 1px solid var(--border);
                    box-shadow: var(--shadow);
                    position: relative;
                    overflow: hidden;
                }
                
                /* Subtle glow effect on app links card */
                .app-links::before {
                    content: "";
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(
                        circle at center,
                        var(--primary-glow) 0%,
                        transparent 80%
                    );
                    opacity: 0.1;
                    z-index: -1;
                }
                
                .app-links-header {
                    color: var(--text);
                    margin-bottom: 1.25rem;
                    text-align: center;
                    font-weight: 500;
                    font-size: 1.1rem;
                    letter-spacing: 0.02em;
                }
                
                .app-links-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 1.1rem;
                    text-align: center;
                }
                
                .app-link {
                    padding: 0;
                    border-radius: 0.75rem;
                    background: rgba(255, 255, 255, 0.03);
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                    border: 1px solid var(--border);
                    position: relative;
                    overflow: hidden;
                }
                
                .app-link:hover {
                    background: var(--card-hover);
                    transform: translateY(-3px) scale(1.02);
                    border-color: var(--border-hover);
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
                }
                
                /* Hover effect for app links */
                .app-link::after {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 0;
                    background: linear-gradient(to bottom, var(--primary-glow), transparent);
                    opacity: 0;
                    transition: all 0.3s ease;
                }
                
                .app-link:hover::after {
                    height: 4px;
                    opacity: 1;
                }
                
                .app-link a {
                    color: var(--primary);
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 1.05rem;
                    display: block;
                    position: relative;
                    z-index: 1;
                    transition: all 0.3s ease;
                    padding: 1.1rem;
                    width: 100%;
                    height: 100%;
                }
                
                .app-link a:hover {
                    color: var(--text);
                }
                
                /* Status indicator dot */
                .status-indicator {
                    display: inline-block;
                    width: 0.55rem;
                    height: 0.55rem;
                    border-radius: 50%;
                    margin-right: 0.4rem;
                    vertical-align: middle;
                }
                
                .status-connected {
                    background: var(--primary);
                    box-shadow: 0 0 8px var(--primary-glow);
                }
                
                .status-disconnected {
                    background: #ff3b30;
                    box-shadow: 0 0 8px rgba(255, 59, 48, 0.4);
                }
                
                /* Gateway discovery card styles */
                .gateway-card {
                    display: flex;
                    align-items: center;
                    padding: 1.1rem 1.5rem;
                    position: relative;
                    overflow: hidden;
                    background: var(--card-bg);
                    border-radius: 1rem;
                    border: 1px solid var(--border);
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                    box-shadow: var(--shadow-sm);
                    margin-bottom: 0.6rem;
                }
                
                .gateway-card:hover {
                    transform: translateY(-3px);
                    border-color: var(--border-hover);
                    background: var(--card-hover);
                    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
                }
                
                .gateway-card::after {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 0;
                    background: linear-gradient(to bottom, var(--primary-glow), transparent);
                    opacity: 0;
                    transition: all 0.3s ease;
                }
                
                .gateway-card:hover::after {
                    height: 4px;
                    opacity: 1;
                }
                
                .gateway-accent {
                    position: absolute;
                    left: 0;
                    top: 10%;
                    height: 80%;
                    width: 4px;
                    background: var(--primary);
                }
                
                .gateway-content {
                    flex-grow: 1;
                    margin-left: 1rem;
                }
                
                .gateway-hostname {
                    font-size: 1.15rem;
                    font-weight: 600;
                    color: var(--primary);
                    margin-bottom: 0.4rem;
                }
                
                .gateway-ip-container {
                    display: flex;
                    align-items: center;
                }
                
                .gateway-ip-label {
                    color: var(--text-secondary);
                    font-size: 0.9rem;
                    font-weight: 500;
                }
                
                .gateway-ip-value {
                    color: var(--text);
                    margin-left: 0.5rem;
                    font-family: monospace;
                    font-size: 0.95rem;
                }
                
                .gateway-button {
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    background: var(--primary-gradient);
                    color: var(--text);
                    text-decoration: none;
                    border-radius: 0.5rem;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    box-shadow: var(--shadow-sm);
                }
                
                .gateway-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
                }
                
                /* Mobile optimizations */
                @media (max-width: 768px) {
                    html {
                        font-size: 100%;
                    }
                    
                    .container {
                        padding: 1.75rem;
                        width: 95%;
                    }
                    
                    .grid, .network-info, .device-grid {
                        grid-template-columns: 1fr;
                    }
                    
                    .app-links-grid {
                        grid-template-columns: 1fr;
                        gap: 0.9rem;
                    }
                    
                    h1 {
                        font-size: 1.9rem;
                    }
                    
                    .header {
                        flex-wrap: wrap;
                        gap: 0.9rem;
                        margin-bottom: 1.75rem;
                        padding-bottom: 1.25rem;
                    }
                    
                    .logo {
                        width: 3.25rem;
                        height: 3.25rem;
                    }
                }
                
                /* Small mobile devices */
                @media (max-width: 480px) {
                    body {
                        padding: 0.65rem;
                    }
                    
                    .container {
                        padding: 1.5rem 1.25rem;
                        width: 100%;
                        border-radius: 1rem;
                    }
                    
                    .device-property {
                        flex-direction: column;
                        align-items: flex-start;
                        margin: 0.85rem 0;
                    }
                    
                    .device-property-value {
                        margin-left: 0;
                        margin-top: 0.3rem;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <svg width="40" height="40" viewBox="0 0 121 120" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo">
                        <circle cx="60.271" cy="60" r="60" fill="#2B2B2B"/>
                        <path d="M36.0973 58.5225L64.1059 24.5269C66.1068 22.0984 70.0209 23.9922 69.3584 27.0683L63.8738 52.5347C63.452 54.4931 65.03 56.3075 67.0281 56.1613L81.1945 55.1247C83.889 54.9276 85.4526 58.1114 83.6494 60.1232L52.2089 95.2009C50.0664 97.5912 46.1723 95.4044 47.0982 92.3309L55.3754 64.8543C56.0222 62.7075 54.173 60.6349 51.9666 61.0337L38.9485 63.3863C36.197 63.8836 34.3193 60.6805 36.0973 58.5225Z" fill="#00d672"/>
                    </svg>
                    <div>
                        <h1>Sourceful Energy Gateway</h1>
                        <div style="font-size: 1rem; color: var(--text-secondary); margin-top: 0.3rem; font-weight: 500;">""" + gateway_name + """</div>
                    </div>
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

        # Add Other Energy Gateways Section right after the app links
        try:
            from server.network.network_utils import NetworkUtils

            # Discover other blixt energy gateways on the network
            other_gateways = NetworkUtils.discover_blixt_devices(scan_duration=3)

            if other_gateways:
                ret += '<div class="section">'
                ret += '<h2>Other Energy Gateways on the Network</h2>'
                ret += '<p style="color: var(--text-secondary); margin-bottom: 0.8rem; font-size: 0.9rem;">These are other Sourceful Energy Gateways discovered on your local network</p>'
                ret += '<div class="device-grid">'

                for gateway in other_gateways:
                    hostname = gateway.get('hostname', 'Unknown')
                    ip = gateway.get('ip', 'Unknown')

                    ret += f'''
                        <div class="gateway-card">
                            <div class="gateway-accent"></div>
                            
                            <div class="gateway-content">
                                <div class="gateway-hostname">{hostname}</div>
                                
                                <div class="gateway-ip-container">
                                    <span class="gateway-ip-label">IP:</span>
                                    <span class="gateway-ip-value">{ip}</span>
                                </div>
                            </div>
                            
                            <div>
                                <a href="http://{hostname}.local" class="gateway-button">
                                    Open Gateway
                                </a>
                            </div>
                        </div>
                    '''
                ret += '</div></div>'
        except Exception as e:
            # Log the error but don't show it to users
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error displaying other gateways: {e}")
            pass

        # Status Section
        ret += '<div class="section">'
        ret += '<div class="grid">'

        # Version and Uptime cards
        try:
            status = state.get('status', {})
            uptime = status.get('uptime', 0)
            days, remainder = divmod(uptime // 1000, 60 * 60 * 24)
            hours, remainder = divmod(remainder, 60 * 60)
            minutes, seconds = divmod(remainder, 60)

            ret += f'''
                <article>
                    <div class="card-header">Version</div>
                    <div class="card-value">{status.get('version', 'N/A')}</div>
                </article>
                <article>
                    <div class="card-header">Uptime</div>
                    <div class="card-value">{int(days):02d} days {int(hours):02d} hours {int(minutes):02d} minutes {int(seconds):02d} seconds</div>
                </article>
            '''
        except Exception:
            ret += f'''
                <article>
                    <div class="card-header">Version</div>
                    <div class="card-value">N/A</div>
                </article>
                <article>
                    <div class="card-header">Uptime</div>
                    <div class="card-value">N/A</div>
                </article>
            '''
        ret += '</div></div>'

        # Devices Section
        ret += '<div class="section">'

        try:
            # Get devices data
            devices = state.get('devices', {})

            # Configured Devices
            configured_devices = devices.get('configured', [])
            if isinstance(configured_devices, list) and configured_devices:
                ret += '<h3>Configured Devices</h3>'
                ret += '<p style="color: var(--text-secondary); margin-bottom: 0.8rem; font-size: 0.9rem;">Those are devices that the gateway is currently connected to</p>'
                ret += '<div class="device-grid">'
                for device in configured_devices:
                    # Safely access device properties
                    name = device.get('name', 'Unknown')
                    device_id = device.get('id', 'Unknown')
                    is_open = device.get('is_open', False)
                    connection = device.get('connection', {})
                    device_type = connection.get('device_type', 'Unknown')
                    ip = connection.get('ip', 'Unknown')
                    port = connection.get('port', 'Unknown')
                    mac = connection.get('mac', 'Unknown')

                    # Try to get hostname from connection or create a hostname from the IP if not available
                    hostname = connection.get('hostname', '')
                    if not hostname and ip and ip != 'Unknown':
                        # If no hostname is available, use the IP's last octet as a simple identifier
                        ip_parts = ip.split('.')
                        if len(ip_parts) == 4:
                            hostname = f"device-{ip_parts[3]}"

                    # Create the display name with hostname in parentheses if available
                    display_name = name
                    if hostname:
                        display_name = f"{name} ({hostname})"

                    ret += f'''
                        <div class="device-card">
                            <div class="card-header">{display_name}</div>
                            <div class="device-details">
                                <div class="device-property">
                                    <span class="device-property-label">ID:</span>
                                    <span class="device-property-value">{device_id}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">Status:</span>
                                    <span class="device-property-value">
                                        <span class="status-indicator status-{'connected' if is_open else 'disconnected'}"></span>
                                        {'Connected' if is_open else 'Disconnected'}
                                    </span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">Type:</span>
                                    <span class="device-property-value">{device_type}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">IP:</span>
                                    <span class="device-property-value">{ip}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">Port:</span>
                                    <span class="device-property-value">{port}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">MAC:</span>
                                    <span class="device-property-value">{mac}</span>
                                </div>
                            </div>
                        </div>
                    '''
                ret += '</div>'

            # Saved Devices
            saved_devices = devices.get('saved', [])
            if isinstance(saved_devices, list) and saved_devices:
                ret += '<h3>Saved Devices</h3>'
                ret += '<p style="color: var(--text-secondary); margin-bottom: 0.8rem; font-size: 0.9rem;">Those are saved device configurations and that the gateway has at some point been connected to</p>'
                ret += '<div class="device-grid">'
                for device in saved_devices:
                    # Safely access device properties
                    name = device.get('name', 'Unknown')
                    device_id = device.get('id', 'Unknown')
                    is_open = device.get('is_open', False)
                    connection = device.get('connection', {})
                    device_type = connection.get('device_type', 'Unknown')
                    ip = connection.get('ip', 'Unknown')
                    port = connection.get('port', 'Unknown')
                    mac = connection.get('mac', 'Unknown')

                    ret += f'''
                        <div class="device-card">
                            <div class="card-header">{name}</div>
                            <div class="device-details">
                                <div class="device-property">
                                    <span class="device-property-label">ID:</span>
                                    <span class="device-property-value">{device_id}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">Type:</span>
                                    <span class="device-property-value">{device_type}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">IP:</span>
                                    <span class="device-property-value">{ip}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">Port:</span>
                                    <span class="device-property-value">{port}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">MAC:</span>
                                    <span class="device-property-value">{mac}</span>
                                </div>
                            </div>
                        </div>
                    '''
                ret += '</div>'

            # Available Hosts Section
            available_hosts = state.get('available_hosts', [])
            if isinstance(available_hosts, list) and available_hosts:
                ret += '<h3>Devices found</h3>'
                ret += '<p style="color: var(--text-secondary); margin-bottom: 0.8rem; font-size: 0.9rem;">Those are devices (inverters specifically) found that could potentially be configured</p>'
                ret += '<div class="device-grid">'
                for host in available_hosts:
                    # Safe dictionary access for host properties
                    ip = host.get('ip', 'Unknown')
                    port = host.get('port', 'Unknown')
                    mac = host.get('mac', 'Unknown')

                    ret += f'''
                        <div class="device-card">
                            <div class="card-header">Host {ip}</div>
                            <div class="device-details">
                                <div class="device-property">
                                    <span class="device-property-label">IP:</span>
                                    <span class="device-property-value">{ip}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">Port:</span>
                                    <span class="device-property-value">{port}</span>
                                </div>
                                <div class="device-property">
                                    <span class="device-property-label">MAC:</span>
                                    <span class="device-property-value">{mac}</span>
                                </div>
                            </div>
                        </div>
                    '''
                ret += '</div>'

            # If no devices were found
            if not (configured_devices or saved_devices or available_hosts):
                ret += '''
                    <article>
                        <div class="card-header">Devices</div>
                        <div class="card-value">N/A</div>
                    </article>
                '''

        except Exception:
            ret += '''
                <article>
                    <div class="card-header">Devices</div>
                    <div class="card-value">N/A</div>
                </article>
            '''

        ret += '</div>'

        # Crypto Section
        ret += '<div class="section">'
        ret += '<div class="grid">'

        try:
            # Get crypto data
            crypto_data = state.get('crypto', {})

            # Only proceed if it's actually a dictionary
            if isinstance(crypto_data, dict):
                for key, value in crypto_data.items():
                    formatted_key = ' '.join(word.capitalize() for word in key.split('_'))
                    ret += f'''
                        <article>
                            <div class="card-header">{formatted_key}</div>
                            <div class="card-value">{value}</div>
                        </article>
                    '''
            else:
                # Just display N/A for mock objects
                ret += f'''
                    <article>
                        <div class="card-header">Crypto Info</div>
                        <div class="card-value">N/A</div>
                    </article>
                '''
        except Exception:
            ret += f'''
                <article>
                    <div class="card-header">Crypto Info</div>
                    <div class="card-value">N/A</div>
                </article>
            '''

        ret += '</div></div>'

        # Network Section
        ret += '<div class="section">'

        try:
            network = state.get('network', {})
            if isinstance(network, dict):
                if 'error' in network:
                    ret += f'''
                        <article>
                            <div class="card-header">Error</div>
                            <div class="card-value">{network.get('error', 'Unknown error')}</div>
                        </article>
                    '''
                else:
                    if 'wifi' in network:
                        wifi = network.get('wifi', {})
                        if isinstance(wifi, dict):
                            ret += '<h3>WiFi</h3>'
                            ret += '<div class="network-info">'
                            ret += f'''
                                <article>
                                    <div class="card-header">Connected SSID</div>
                                    <div class="card-value">{wifi.get('connected', 'Not connected')}</div>
                                </article>
                            '''
                            ssids = wifi.get('ssids', [])
                            if isinstance(ssids, list) and ssids:
                                ret += '''
                                    <article>
                                        <div class="card-header">Available Networks</div>
                                        <div class="card-value">
                                '''
                                ret += '<br>'.join(ssids)
                                ret += '</div></article>'
                            ret += '</div>'

                    if 'address' in network:
                        addr = network.get('address', {})
                        if isinstance(addr, dict):
                            ret += '<h3>Network Addresses</h3>'
                            ret += '<div class="network-info">'
                            for key in ['ip', 'port', 'eth0_mac', 'wlan0_mac']:
                                if key in addr:
                                    ret += f'''
                                        <article>
                                            <div class="card-header">{key.replace('_', ' ').upper()}</div>
                                            <div class="card-value">{addr.get(key, 'Unknown')}</div>
                                        </article>
                                    '''
                            ret += '</div>'

                            interfaces = addr.get('interfaces', {})
                            if isinstance(interfaces, dict) and interfaces:
                                ret += '<h3>Network Interfaces</h3>'
                                ret += '<div class="network-info">'
                                for interface, ip in interfaces.items():
                                    ret += f'''
                                        <article>
                                            <div class="card-header">{interface}</div>
                                            <div class="card-value">{ip}</div>
                                        </article>
                                    '''
                                ret += '</div>'
            else:
                ret += '''
                    <article>
                        <div class="card-header">Network</div>
                        <div class="card-value">N/A</div>
                    </article>
                '''
        except Exception:
            ret += '''
                <article>
                    <div class="card-header">Network</div>
                    <div class="card-value">N/A</div>
                </article>
            '''

        ret += '</div>'

        # Messages Section
        try:
            status = state.get('status', {})
            if isinstance(status, dict):
                messages = status.get('messages', [])
                if isinstance(messages, list) and messages:
                    ret += '<div class="section">'
                    ret += '<h2>Messages</h2>'
                    ret += '<div class="messages">'
                    for msg in messages:
                        if isinstance(msg, dict):
                            msg_type = msg.get('type', 'info')
                            message = msg.get('message', 'No message')
                            message_text = message
                            if isinstance(message, list) and message:
                                try:
                                    message_text = message[0] % tuple(message[1:])
                                except:
                                    message_text = str(message)
                            ret += f'''
                                <div class="message {msg_type}">
                                    {message_text}
                                </div>
                            '''
                    ret += '</div></div>'
        except Exception:
            # Don't add messages section if there's an error
            pass

        ret += "</div></body></html>"
        return 200, ret
