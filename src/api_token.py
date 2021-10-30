import requests
import time
import config


class ApiToken:
    def __init__(self):
        self.json = self.get()

    def get(self):
        resp = requests.post(config.token_url, config.params)
        status = resp.status_code
        resp.raise_for_status()
        return resp.json()

    def refresh(self):
        self.json = self.get()

    def __str__(self):
        return str(self.json['access_token'])

    def __repr__(self):
        return self.__str__()
