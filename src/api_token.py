import requests
import time
from . import config


class ApiToken:
    def __init__(self, uid: str="", secret: str=""):
        self.__params = config.params.copy()
        if uid and secret:
            self.__params['client_id'] = uid
            self.__params['client_secret'] = secret
        self.json = self.get()

    def get(self):
        resp = requests.post(config.token_url, self.__params)
        status = resp.status_code
        resp.raise_for_status()
        return resp.json()

    def refresh(self):
        self.json = self.get()

    def __str__(self):
        return str(self.json['access_token'])

    def __repr__(self):
        return self.__str__()
