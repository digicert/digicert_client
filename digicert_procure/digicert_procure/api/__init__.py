#!/usr/bin/env python

import json
from urllib import urlencode

from ..https import VerifiedHTTPSConnection
from ..api.responses import RequestFailedResponse


class Request(object):
    def __init__(self, action, host, conn=None):
        self.action = action
        self.host = host
        self.conn = conn if conn is not None else VerifiedHTTPSConnection(host)

    def send(self):
        self.conn.request(self.action.get_method(),
                          self.action.get_path(),
                          self.action.get_params(),
                          self.action.get_headers())
        conn_rsp = self.conn.getresponse()
        payload = json.loads(conn_rsp.read())
        response = self.action.process_response(conn_rsp.status, conn_rsp.reason, payload)
        self.conn.close()
        return response


class Action(object):
    _headers = {'Accept': 'application/json'}

    def __init__(self, customer_api_key, customer_name=None, **kwargs):
        self.customer_api_key = customer_api_key
        if customer_name is not None:
            self.customer_name = customer_name
        for key, value in kwargs.items():
            if not self._process_special(key, value):
                setattr(self, key, value)

    def _process_special(self, key, value):
        pass

    def set_header(self, key, value):
        self._headers[key] = value

    def get_params(self):
        params = {}
        for param, value in self.__dict__.items():
            if not param.startswith('_'):
                params[param] = value
        return urlencode(params)

    def get_headers(self):
        return self._headers

    def get_method(self):
        raise NotImplementedError

    def _subprocess_response(self, status, reason, response):
        raise NotImplementedError

    def _is_failure_response(self, response):
        return response['response']['result'] == 'failure'

    def process_response(self, status, reason, response):
        if status >= 300:
            return RequestFailedResponse([{'status': status, 'reason': reason}])
        try:
            if self._is_failure_response(response):
                return RequestFailedResponse(response['response']['error_codes'])
            return self._subprocess_response(status, reason, response)
        except KeyError:
            return RequestFailedResponse([{'result': 'unknown failure', 'response': str(response)}])


if __name__ == '__main__':
    pass