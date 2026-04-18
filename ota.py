import os
import gc
import time

import requests
import logging

class OTA:
    FILE_SUFFIX = ".ota"

    def __init__(self, github_repo, github_branch):
        self.logger = logging.getLogger("OTA")
        self.github_repo = github_repo
        self.github_branch = github_branch
        self.headers = {
            "User-Agent": self.github_repo,
        }

    def run(self):
        try:
            # Free some memory before the first HTTP call returns a large JSON payload
            gc.collect()
            time.sleep(3)
            files = self._get_files_list()
            self.logger.info(f"Downloading {len(files)} files")

            for path in files:
                self.logger.info(path)
                self._download(path)

            self.logger.info(f"Updating {len(files)} files")

            for path in files:
                os.rename(path + self.FILE_SUFFIX, path)

            self.logger.info("success")

        except Exception as e:
            self.logger.exception("failed", e)

    def _get_files_list(self):
        url = f"https://api.github.com/repos/{self.github_repo}/git/trees/{self.github_branch}?recursive=1"
        response = requests.get(url, headers=self.headers)
        try:
            if not response.status_code == 200:
                raise RuntimeError(f"GET {url} returned {response.status_code}: {response.text}")

            return [
                item["path"]
                for item in response.json()["tree"]
                if item["type"] == "blob" and item["path"].endswith(".py")
            ]
        finally:
            response.close()

    def _download(self, path):
        url = f"https://raw.githubusercontent.com/{self.github_repo}/{self.github_branch}/{path}"
        self._mkdir_parent(path)
        response = requests.get(url, headers=self.headers)

        try:
            if not response.status_code == 200:
                raise RuntimeError(f"GET {url} returned {response.status_code}: {response.text}")

            with open(path + self.FILE_SUFFIX, "wb") as f:
                while True:
                    chunk = response.raw.read(2048)
                    if not chunk:
                        break
                    f.write(chunk)
        finally:
            response.close()

    def _mkdir_parent(self, path):
        parts = path.split("/")[:-1]
        current = ""
        for part in parts:
            current = current + "/" + part
            try:
                os.mkdir(current)
            except OSError:
                pass # if directory exists
