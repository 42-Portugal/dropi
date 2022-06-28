import time
import requests
from . import config


class ApiToken:
    """A 42 intra api authentication token.

    Can be instanciated without optional args from :mod:`~dropi.config`
    values, but if one optional arg is supplied, both need to be. Otherwise
    values from :mod:`~dropi.config` will be used.

    If printed or converted to string, the value of the `access_token` key
    from the response dict stored in :attr:`~.ApiToken.json` will be printed
    or returned.

    Args:
        uid (str, optional): the `client_id` from 42 app
        secret (str, optional): the `client_secret` from 42 app

    Attributes:
        json (dict): A dictionary containing the response from the token
            request.

    """

    def __init__(self, uid: str = "", secret: str = ""):
        self.params = config.params.copy()
        if uid != "" and secret != "":
            self.params['client_id'] = uid
            self.params['client_secret'] = secret
        self.json = self.get()
        self.fetched_at = int(time.time())

    def needs_refresh(self):
        """Check if the token needs refreshing

        Returns:
            bool: true if the token's life is less then 2 second, false otherwise
        """
        return (self.json['expires_in'] - (int(time.time()) - self.fetched_at)) <= 2

    def get(self):
        """Gets a new token from 42 intra's api.

        Raises:
            HTTPError: Request has failed.

        Returns:
            dict: A dictionary containing the 42 intra's api response.

        """
        resp = requests.post(config.token_url, self.params)
        status = resp.status_code
        resp.raise_for_status()
        return resp.json()

    def refresh(self):
        """Updates the stored token.

        If needed, sleeps up to 2 seconds to wait for the token to expire on the
        server. Uses :meth:`~.ApiToken.get` and store result in
        :attr:`~.ApiToken.json` updating :attr:`~.ApiToken.fetched_at`

        Raises:
            HTTPError: Request has failed
        """
        left = self.json['expires_in'] - (time.time() - self.fetched_at)
        if left > 0 and left <= 2:
            time.sleep(left)
        self.json = self.get()
        self.fetched_at = int(time.time())

    def __str__(self):
        return str(self.json['access_token'])

    def __repr__(self):
        return self.__str__()
