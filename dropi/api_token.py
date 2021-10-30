import requests
import time
from . import config


class ApiToken:
    """A 42 intra api authentication token.
    
    Args:
        uid (str, optional): the `client_id` from 42 app
        secret (str, optional): the `client_secret` from 42 app

    Attributes:
        json (dict): A dictionary containing the token to be provided.
    """
    def __init__(self, uid: str="", secret: str=""):
        self.__params = config.params.copy()
        if uid and secret:
            self.__params['client_id'] = uid
            self.__params['client_secret'] = secret
        self.json = self.get()

    def get(self):
        """Gets a new token from 42 intra api.

        Raises:
            HTTPError: Request has failed

        Returns:
            dict: A dictionary containing the token to be provided.
        """
        resp = requests.post(config.token_url, self.__params)
        status = resp.status_code
        resp.raise_for_status()
        return resp.json()

    def refresh(self):
        """Updates the stored token.

        Raises:
            HTTPError: Request has failed
        """
        self.json = self.get()

    def __str__(self):
        return str(self.json['access_token'])

    def __repr__(self):
        return self.__str__()
