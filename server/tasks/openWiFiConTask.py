import logging
import time
import socket
import subprocess
import os
from urllib.request import urlopen
from server.network.wifi import WiFiHandler, is_connected, get_ip_address
from server.app.blackboard import BlackBoard
from server.tasks.saveStateTask import SaveStateTask
from server.tasks.scanWiFiTask import ScanWiFiTask

from .task import Task


log = logging.getLogger(__name__)


class OpenWiFiConTask(Task):
    def __init__(self, event_time: int, bb: BlackBoard, wificon: WiFiHandler):
        super().__init__(event_time, bb)
        self.wificon = wificon
        self.retries = 3
        self.connectivity_timeout = 30  # seconds
        self.fallback_dns = ['8.8.8.8', '1.1.1.1']  # Google DNS and Cloudflare DNS
        log.debug("Initialized OpenWiFiConTask for SSID: %s with %d retries and %d seconds timeout", 
                 self.wificon.ssid, self.retries, self.connectivity_timeout)

    def _configure_dns(self):
        """Configure DNS settings using multiple methods."""
        try:
            log.debug("Configuring DNS settings...")
            
            # Method 1: Try to get DNS from host
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    current_dns = f.read()
                log.debug("Current DNS configuration: %s", current_dns)
            except Exception as e:
                log.warning("Could not read current DNS config: %s", str(e))

            # Method 2: Write fallback DNS servers
            try:
                with open('/etc/resolv.conf', 'w') as f:
                    # Add search domain if available
                    f.write("search local\n")
                    # Add Google and Cloudflare DNS servers
                    for dns in self.fallback_dns:
                        f.write(f"nameserver {dns}\n")
                log.debug("Added fallback DNS servers")
            except Exception as e:
                log.error("Failed to write DNS configuration: %s", str(e))

            # Method 3: Update nsswitch.conf if it exists
            nsswitch_path = '/etc/nsswitch.conf'
            if os.path.exists(nsswitch_path):
                try:
                    with open(nsswitch_path, 'r') as f:
                        lines = f.readlines()
                    
                    with open(nsswitch_path, 'w') as f:
                        for line in lines:
                            if line.startswith('hosts:'):
                                f.write('hosts: files dns\n')
                            else:
                                f.write(line)
                    log.debug("Updated nsswitch.conf")
                except Exception as e:
                    log.error("Failed to update nsswitch.conf: %s", str(e))

            # Method 4: Flush DNS cache
            try:
                subprocess.run(['nscd', '-K'], check=False)
                subprocess.run(['nscd'], check=False)
            except Exception as e:
                log.debug("nscd commands failed (this is normal if nscd is not installed): %s", str(e))

            # Method 5: Restart system DNS resolver
            try:
                subprocess.run(['kill', '-HUP', '1'], check=True)
                log.debug("Sent SIGHUP to init process")
            except Exception as e:
                log.error("Failed to send SIGHUP: %s", str(e))

            return True
        except Exception as e:
            log.error("DNS configuration failed: %s", str(e))
            return False

    def _verify_network_connectivity(self) -> bool:
        """Verify network connectivity by checking DNS and HTTP access."""
        try:
            log.debug("Starting network connectivity verification...")
            
            # First try: DNS resolution using system resolver
            try:
                log.debug("Attempting DNS resolution for google.com...")
                ip = socket.gethostbyname('google.com')
                log.debug("DNS resolution successful: google.com -> %s", ip)
            except socket.gaierror as e:
                log.warning("System DNS resolution failed: %s", str(e))
                # Try direct DNS query to fallback servers
                for dns in self.fallback_dns:
                    try:
                        socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect((dns, 53))
                        log.debug("Direct DNS connection to %s successful", dns)
                        return True
                    except Exception as e:
                        log.warning("Failed to connect to DNS %s: %s", dns, str(e))
                return False
            
            # Try HTTP connection
            try:
                log.debug("Attempting HTTP connection to google.com...")
                urlopen('http://google.com', timeout=5)
                log.debug("HTTP connection successful")
                return True
            except Exception as e:
                log.warning("HTTP connection failed: %s", str(e))
                # If DNS worked but HTTP failed, still return True as it might be a temporary issue
                return True
                
        except Exception as e:
            log.warning("Network connectivity check failed: %s", str(e))
            return False

    def _wait_for_network(self, timeout: int) -> bool:
        """Wait for network to be fully configured with timeout."""
        log.debug("Starting network wait sequence with %d seconds timeout", timeout)
        start_time = time.time()
        attempt = 1
        dns_configured = False
        
        while time.time() - start_time < timeout:
            log.debug("Network check attempt %d", attempt)
            
            if not is_connected():
                log.debug("Network Manager reports no connection, waiting...")
                time.sleep(1)
                attempt += 1
                continue

            ip = get_ip_address()
            log.debug("Current IP address: %s", ip)
            
            if ip == '0.0.0.0':
                log.debug("Invalid IP address (0.0.0.0), waiting...")
                time.sleep(1)
                attempt += 1
                continue

            # Configure DNS if not done yet
            if not dns_configured:
                log.debug("Configuring DNS...")
                dns_configured = self._configure_dns()
                if not dns_configured:
                    log.warning("DNS configuration failed")
                time.sleep(2)  # Give DNS configuration time to take effect

            log.debug("Valid IP obtained, verifying connectivity...")
            if self._verify_network_connectivity():
                log.debug("Network is fully configured and operational")
                return True

            log.debug("Network verification failed, waiting...")
            time.sleep(1)
            attempt += 1
            
        log.warning("Network wait sequence timed out after %d seconds", timeout)
        return False

    def execute(self, event_time):
        log.info("Starting WiFi connection process to %s", self.wificon.ssid)
        try:
            log.debug("Attempting to connect to WiFi network...")
            if self.wificon.connect():
                log.debug("Initial WiFi connection successful, waiting for network configuration...")
                # Wait for network to be fully configured
                if self._wait_for_network(self.connectivity_timeout):
                    log.debug("Network configuration complete")
                    self.bb.add_info(f"Connected to WiFi: {self.wificon.ssid}")
                    
                    # Restart websocket connection
                    log.debug("Restarting WebSocket connection...")
                    from server.web.socket.settings_subscription import GraphQLSubscriptionClient
                    subscription = GraphQLSubscriptionClient.getInstance(self.bb, self.bb.settings.api.ws_endpoint)
                    subscription.restart_async()
                    log.debug("WebSocket connection restart initiated")
                    
                    return None
                else:
                    log.warning("Network configuration failed after successful WiFi connection")
                    self.bb.add_warning("Connected to WiFi but no internet access")
                    if self.retries > 0:
                        self.retries -= 1
                        log.debug("Scheduling retry (%d remaining) in 10 seconds", self.retries)
                        self.time = event_time + 10000  # Retry in 10 seconds
                        return self
            else:
                log.warning("WiFi connection failed, possibly due to invalid credentials")
                self.bb.add_warning(f"Failed to connect to WiFi: {self.wificon.ssid}. Could be an invalid password.")
            return None
        except Exception as e:
            log.exception("Unexpected error during WiFi connection process")
            self.retries -= 1
            if self.retries > 0:    
                log.debug("Scheduling retry (%d remaining) in 10 seconds", self.retries)
                self.bb.add_error(f"Failed to connect to WiFi: {self.wificon.ssid}. Retry in 10 seconds")
                self.time = event_time + 10000
                return self
            else:
                log.error("All retries exhausted, giving up")
                self.bb.add_error(f"Failed to connect to WiFi: {self.wificon.ssid}. Giving up")
                return None

