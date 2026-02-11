import network
import time

class WiFi:
    MAX_WAIT_TIME = 10

    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        retries = 0

        self.wlan.active(True)
        if self.wlan.isconnected():
            print("Already connected.")
            return True
            
        print(f"Connecting to '{self.ssid}'")
        self.wlan.connect(self.ssid, self.password)
        
        while not self.wlan.isconnected() and retries < self.MAX_WAIT_TIME:
            retries += 1
            print(f"Waiting {retries}/{self.MAX_WAIT_TIME}...")
            time.sleep(1)
        
        if self.wlan.isconnected():
            ip, _, gateway, dns = self.wlan.ifconfig()
            print("Connected successfully")
            print("  IP:      ", ip)
            print("  Gateway: ", gateway)
            print("  DNS:     ", dns)
            return True
        
        else:
            print(f"Failed to connect to Wi-Fi after {retries} attempts.")
            return False
    
    def get_ip(self):
        ip, _, _, _ = self.wlan.ifconfig()
        return ip