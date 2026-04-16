import ntptime
import logging


class NTP:
    DEFAULT_HOST = "pool.ntp.org"

    def __init__(self, host=DEFAULT_HOST):
        self.logger = logging.getLogger("NTP")
        self.host = host

    def sync(self):
        try:
            self.logger.info(f"Syncing time with {self.host}")
            ntptime.host = self.host
            ntptime.settime()
            return True
        except Exception as e:
            self.logger.exception("Could not sync time", e)
            return False
