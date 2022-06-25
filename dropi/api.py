#TODO: fix return type from requests methods, the wrapper should call
# response.json()

import requests
import time

from multiprocessing.pool import ThreadPool
from math import ceil
from typing import TypedDict

from . import config, api_token


class ApiRequest(TypedDict):
    """A TypedDict to represent requests to 42 intra's api.

    .. code-block:: python
        :linenos:

        # The following code will get all users from campus 38 (lisbon) from the api
        # and give each one evaluation point using the mass_request method
        import dropi

        api = dropi.Api42()
        users = api.get("campus/38/users")

        # generate a list of ApiRequest dicts for the request:
        reqs = [{
                'endpoint': f'users/{u["login"]}/correction_points/add',
                'payload': {"id": u["login"], "reason": "Staff is testing stuff"},
                } for u in users]

        #This will run run the request concurrently
        api.mass_request("POST", reqs)

        #Or if you want them to be ran one by one:
        api.mass_request("POST", reqs, multithreaded=False)

        #Should apply filter
    """
    endpoint: str
    """The request's endpoint, without the ``https://intra.42.fr/v2/`` prefix.

        Empty endpoints will raise an exception.
    """
    payload: dict
    """The request's payload. Can be empty"""


class Api42:
    """An interface to request 42 intra's api.

    Provides wrappers for GET, POST, PATCH & DELETE methods.

    The :meth:`~.Api42.mass_request` method provides an easy way of running
    a large amount of requests, concurrently or not depending on provided
    options.

    Args:
        token (:class:`~.ApiToken`): See :class:`~.ApiToken`.
        log_lvl (:class:`~.LogLvl`, optional): See :class:`~.LogLvl` for more
            infos. Optional, defaults to :attr:`~.LogLvl.Info`.
        raises (bool): Set to false to ignore exceptions. Defaults to ``true``

    Attributes:
        token (:class:`~.ApiToken`): An access token from 42 intra's api
            to authenticate requests.
        headers (dict): The headers to be provided with requests. They are
            generated at instanciation based on the values from
            :mod:`~.config` and :class:`~.ApiToken`.

    """

    def __init__(self,
                 token: api_token.ApiToken = None,
                 log_lvl: config.LogLvl = config.log_lvl,
                 raises: bool = True):
        self.token = token if token else api_token.ApiToken()
        self._log_lvl = log_lvl
        self._raises = raises
        self.headers = {"Authorization": f"Bearer {self.token}", }

    def _log(self, lvl, msg):
        print(f"[dropi - {lvl}]: {msg}")

    def _fatal(self, msg):
        if self._log_lvl > config.LogLvl.Fatal:
            return
        self._log("FATAL", msg)

    def _error(self, msg):
        if self._log_lvl > config.LogLvl.Error:
            return
        self._log("ERROR", msg)

    def _debug(self, msg):
        if self._log_lvl > config.LogLvl.Debug:
            return
        self._log("DEBUG", msg)

    def _info(self, msg):
        if self._log_lvl > config.LogLvl.Info:
            return
        self._log("INFO", msg)

    def _refresh_token(self):
        self.token.refresh()
        self.headers = {"Authorization": f"Bearer {self.token}", }

    def handler(func):
        """Handles a request.

        Each request uses a private method to send request to 42 intra's api.
        This function is a decorator for these private methods.

        It checks for a valid ApiRequest (built using the `url', `payload` and `params` arguments)
        and refreshes the token automatically if needed before running the request, and
        then run the request inside a try/except block. If
        :data:`~.raises` is set to ``False``, it will ignore possible
        ``RequestsException``

        Raises:
            TypeError: for invalid ApiRequest
            RequestException: if an error occured when sending request


        To do:
            More granular exceptions handling (eg: ``Timeout``, ``HTTPError``
            or ``ConnectionError`` could be retried, etc).

            Fix the logic to check if token needs refresh, it's doesn't work
            since token infos doesn't get updated.

        """
        def _handle(self, request: ApiRequest):
            try:
                if not isinstance(request, dict) \
                    and "payload" not in request \
                    and "endpoint" not in request:
                    raise TypeError("request must be an ApiRequest")

                if self.token.json['expires_in'] <= 10:
                    self._refresh_token()

                self._debug(f"sending request-> {request}")

                resp = func(self, request)
                resp.raise_for_status()
                self._debug(f"after request -> {resp.status_code}")
                return resp.json() if resp.content else {}
            except requests.exceptions.RequestException as e:
                self._error(e)
                if self._raises:
                    raise e
            except Exception as e:
                # Always raise others, unexpected exceptions. Including
                # TypeError from request's dictionary's key check
                self._error(e)
                raise e
        return _handle

    def build_url_from_params(self, params):
        append = ""
        for p in ["sort", "filter", "range"]:
               if p in params:
                for k, v in params[p].items():
                    if append:
                        append += '&'
                    append += f"{p}[{k}]={v}"
        if append:
            return "?" + append
        return ""

    @handler
    def _get(self, req: ApiRequest):
        return requests.get(f"{config.endpoint}/{req['endpoint']}",
                            headers=self.headers,
                            json=req['payload'],
                            params=req['params'] if 'params' in req else {})

    def get(self,
            url: str,
            data: dict = {},
            params: dict = {},
            scrap: bool = True,
            multithreaded: bool = True):
        """Sends a GET request to 42 intra's api.

        Args:
            url (string): the requested URL, without the api.intra.42.fr/v2 prefix
            data (dict): the request's payload
            params (dict): the request's parameters
            scrap (bool, optional): If ``True``, will fetch all pages of
                result. Defaults to ``True``
            multithreaded (bool, optional): If ``True`` and scrap is enabled,
                will fetch all pages concurrently (see :meth:`~.mass_request`
                for more details). Defaults to ``True``
        """

        # For the case of GET requests, we'll need to retrieve the headers
        # from the response to check for additionnal pages.
        # Since all Api42 wrapper functions return only the content of
        # the response as dict, we'll use the requests.get method directly
        # to know the numbers of pages (if more than one page of result).
        url = url + self.build_url_from_params(params)
        r = requests.get(f"https://api.intra.42.fr/v2/{url}",
                        json=data,
                        headers=self.headers)

        r.raise_for_status()

        res = r.json()
        if 'x-total' in r.headers and scrap is True:
            npage = int(r.headers['x-total']) / int(r.headers['x-per-page'])
            npage = ceil(npage)

            reqs = []
            for i in range(2, npage + 1):
                pl = {}
                pl.update(data)
                pl['page'] = {'number': i}
                reqs.append({'endpoint': url,
                    'payload': pl,
                    'params': params
                })

            res.extend(
                self.mass_request(
                    "GET",
                    reqs,
                    multithreaded=multithreaded))

        return res

    @handler
    def _post(self, req: ApiRequest):
        if 'files' in req:
            return requests.post(f"{config.endpoint}/{req['endpoint']}",
                            headers=self.headers,
                            json=req['payload'],
                            files=req['files'])

        return requests.post(f"{config.endpoint}/{req['endpoint']}",
                            headers=self.headers,
                            json=req['payload'])

    def post(self, url: str, data: dict = {}, params: dict = {}, files = None):
        """Sends a POST request to 42 intra's api.

        To send many POST requests at once, see: :meth:`~.mass_request`.

        Args:
            url (string): the requested URL, without the api.intra.42.fr/v2 prefix
            data (dict): the request's payload
            params (dict): the request's parameters
            files (os.File): a file to be uploaded
        """
        return self._post({'endpoint': url, 'payload': data, 'params': params, 'files': files})

    @handler
    def _delete(self, request: ApiRequest):
        return requests.delete(f"{config.endpoint}/{request['endpoint']}",
                            headers=self.headers,
                            json=request['payload'])

    def delete(self, url: str, data: dict={}, params: dict={}):
        """Sends a DELETE request to 42 intra's api.

        To send many DELETE requests at once, see: :meth:`~.mass_request`.

        Args:
            url (string): the requested URL, without the api.intra.42.fr/v2 prefix
            data (dict): the request's payload
            params (dict): the request's parameters
        """
        return self._delete({'endpoint': url, 'payload': data, 'params': params})

    @handler
    def _patch(self, request: ApiRequest):
        return requests.patch(f"{config.endpoint}/{request['endpoint']}",
                           headers=self.headers,
                           json=request['payload'])

    def patch(self, url: str, data: dict={}, params: dict={}):
        """Sends a PATCH request to 42 intra's api.

        To send many PATCH requests at once, see: :meth:`~.mass_request`.

        Args:
            url (string): the requested URL, without the api.intra.42.fr/v2 prefix
            data (dict): the request's payload
            params (dict): the request's parameters
        """
        return self._patch({'endpoint': url, 'payload': data, 'params': params})

    def put(self, url: str, data: dict={}, params: dict={}):
        """Sends a PUT request to 42 intra's api.

        To send many PUT requests at once, see: :meth:`~.mass_request`.

        Args:
            url (string): the requested URL, without the api.intra.42.fr/v2 prefix
            data (dict): the request's payload
            params (dict): the request's parameters
        """
        return self._patch({'endpoint': url, 'payload': data, 'params': params})

    def mass_request(self,
                     req_type: str,
                     requests: list[ApiRequest],
                     multithreaded: bool = True):
        """Runs a list of requests to 42 intra's api.

        If one of  the requests fail, an exception will be raised and
        requests will stop being sent.

        ``requests`` must be all be of the same ``req_type``.


        Args:
            req_type (str): The request type, must be one of ``GET``/``POST``/
                ``PATCH``/``DELETE``
            requests (list of :class:`~.ApiRequest`): A list of requests to
                be ran.
            multithreaded (bool, optional): If set to ``True``, requests will
                be ran in one or more multiprocessing pool of size, see :
                :data:`~.max_poolsize`
        """

        if req_type == "GET":
            req_func = self._get
        elif req_type == "POST":
            req_func = self._post
        elif req_type == "PATCH":
            req_func = self._patch
        elif req_type == "DELETE":
            req_func = self._delete
        else:
            raise Exception(f"Invalid or empty request type '{req_type}'")

        res = []

        if multithreaded is True:
            def chunks(lst, n):
                """Yield successive n-sized chunks from lst."""
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]

            pools = chunks(requests, config.max_poolsize)

            delta_time = 0
            start_time = 0

            for p in pools:

                if start_time > 0:
                    delta_time = 1.1 - (time.time() - start_time)
                if delta_time > 0:
                    time.sleep(delta_time)
                start_time = time.time()

                thpool = ThreadPool(processes=len(p))
                reqs = []
                for req in p:
                    if 'params' not in req:
                        req['params'] = {}
                    reqs.append(
                        thpool.apply_async(
                            req_func,
                            (req,))
                    )

                resp_dicts = [r.get() for r in reqs]
                pres = []
                thpool.close()
                for i in range(len(resp_dicts)):
                    if isinstance(resp_dicts[i], list):
                        pres.extend(resp_dicts[i])
                    else:
                        pres.append(resp_dicts[i])

                res.extend(pres)

        else:
            for req in requests:
                res.extend(req_func(req).json())

        return res
