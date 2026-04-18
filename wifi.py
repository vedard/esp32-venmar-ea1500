import network
import time
import logging


class WiFi:
    MAX_WAIT_TIME = 10

    def __init__(self, ssid, password):
        self.logger = logging.getLogger("WiFi")
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        retries = 0

        self.wlan.active(True)
        if self.wlan.isconnected():
            self.logger.info("Already connected")
            return True
            
        self.logger.info(f"Connecting to '{self.ssid}'")
        self.wlan.connect(self.ssid, self.password)
        
        while not self.wlan.isconnected() and retries < self.MAX_WAIT_TIME:
            retries += 1
            self.logger.info(f"Waiting {retries}/{self.MAX_WAIT_TIME}")
            time.sleep(1)
        
        if self.wlan.isconnected():
            ip, _, gateway, dns = self.wlan.ifconfig()
            self.logger.info("Connected successfully")
            self.logger.info(f"IP: {ip}")
            self.logger.info(f"Gateway: {gateway}")
            self.logger.info(f"DNS: {dns}")
            return True
        
        self.logger.error(f"Failed to connect after {retries} attempts")
        return False
    
    def get_ip(self):
        ip, _, _, _ = self.wlan.ifconfig()
        return ip
