import json


def merge(dict1, dict2):
    """Recursively merges dict2 into dict1"""
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for k in dict2:
        if k in dict1:
            dict1[k] = merge(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict1


class Storage:
    CONFIG_FILE = "config.json"
    SECRETS_FILE = "secrets.json"
    STATE_FILE = "data.json"

    def __init__(self, default_state):
        self._options = {}
        self._secrets = {}
        self._state = default_state

        self._load(self.SECRETS_FILE, self._secrets)
        self._load(self.CONFIG_FILE, self._options)
        self._load(self.STATE_FILE, self._state)

    def _load(self, filename, target):
        print(f"Loading {filename}")
        try:
            with open(filename, "r") as f:
                merge(target, json.load(f))
        except:
            print(f"Could not open {filename}")

    def _save_state(self):
        print(f"Saving {self.STATE_FILE}")
        with open(self.STATE_FILE, "w") as f:
            json.dump(self._state, f)

    def get_option(self, key):
        return self._options[key]

    def get_secret(self, key):
        return self._secrets[key]

    def get_persistent_value(self, key):
        return self._state[key]

    def save_persistent_value(self, key, value):
        if key not in self._state:
            raise ValueError("Not a valid state")

        self._state[key] = value
        self._save_state()
