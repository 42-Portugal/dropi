import requests
import time

from multiprocessing.pool import ThreadPool
from math import ceil
from typing import TypedDict
from enum import IntEnum

from . import config, api_token



class ApiRequest(TypedDict):
    endpoint: str
    payload: dict


class LogLvl(IntEnum):
    NoLog = 0
    Debug = 10
    Info = 20
    Error = 30
    Fatal = 40


class Api42:
    def __init__(self, token: api_token.ApiToken,
            log_lvl: LogLvl = LogLvl.Debug, raises: bool = True):
        self.token = token
        self.log_lvl = log_lvl
        self.raises = raises
        self.headers = {"Authorization": f"Bearer {self.token}", }


    def _log(self, lvl, msg):
        print(f"[dropi] {lvl}: {msg}")

    def fatal(self, msg):
        if self.log_lvl > LogLvl.Fatal:
            return
        self._log("FATAL", msg)

    def error(self, msg):
        if self.log_lvl > LogLvl.Error:
            return
        self._log("ERROR", msg)

    def debug(self, msg):
        if self.log_lvl > LogLvl.Debug:
            return
        self._log("DEBUG", msg)

    def info(self, msg):
        if self.log_lvl > LogLvl.Info:
            return
        self._log("INFO", msg)


    def refresh_token(self):
        self.token.refresh()
        self.headers = {"Authorization": f"Bearer {self.token}", }


    def handler(func):
        def _handle(self, *args, **kwargs):
            try:
                if self.token.json['expires_in'] <= 10:
                    self.refresh_token()

                self.debug(f"request-> {args}, {kwargs}")

                resp = func(self, *args, **kwargs)
                resp.raise_for_status()
                return resp

            except Exception as e:
                self.error(e)
                if self.raises:
                    raise e
        return _handle

    @handler
    def _get(self, request: ApiRequest):
        return requests.get(f"{config.endpoint}/{request['endpoint']}",
                            headers=self.headers,
                            json=request['payload'])

    def get(self,
            request: ApiRequest,
            scrap: bool = True,
            multithreaded: bool = True):
        r = self._get(request)
        res = r.json()

        if 'x-total' in r.headers and scrap is True:
            npage = int(r.headers['x-total']) / int(r.headers['x-per-page'])
            npage = ceil(npage)

            reqs = []
            for i in range(2, npage + 1):
                pl = {}
                pl.update(request['payload'])
                pl['page'] = {'number': i}
                reqs.append({'endpoint':request['endpoint'], 'payload': pl})
            res.extend(
                self.mass_request(
                    "GET",
                    reqs,
                    multithreaded=multithreaded))

        return res

    @handler
    def post(self, request: ApiRequest):
        r = requests.post(f"{config.endpoint}/{request['endpoint']}",
                          headers=self.headers,
                          json=request['payload'])
        r.raise_for_status()
        return r.json()

    @handler
    def delete(self, request: ApiRequest):
        r = requests.delete(f"{config.endpoint}/{request['endpoint']}",
                          headers=self.headers,
                          json=request['payload'])
        r.raise_for_status()
        return r.json()

    @handler
    def patch(self, request: ApiRequest):
        r = requests.patch(f"{config.endpoint}/{request['endpoint']}",
                          headers=self.headers,
                          json=request['payload'])
        r.raise_for_status()
        return r.json()

    def mass_request(self,
            req_type: str,
            requests: list[ApiRequest],
            multithreaded: bool = True):

        if req_type == "GET":
            req_func = self._get
        elif req_type == "POST":
            req_func = self.post
        elif req_type == "PATCH":
            req_func = self.patch
        elif req_type == "DELETE":
            req_func = self.delete
        else:
            raise Exception(f"Invalid request type '{req_type}'")

        res = []

        if multithreaded is True:
            def chunks(lst, n):
                """Yield successive n-sized chunks from lst."""
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]

            pools = chunks(requests, config.max_poolsize)
            for p in pools:
                thpool = ThreadPool(processes=len(p))
                reqs = []
                for req in p:
                    reqs.append(
                        thpool.apply_async(
                            req_func,
                            (req), {})
                        )

                resp_dicts = [r.get().json() for r in reqs]
                pres = []

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
