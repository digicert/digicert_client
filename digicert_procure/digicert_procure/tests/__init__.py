#!/usr/bin/env python

import json


class MockResponse:
    def __init__(self, status, reason, payload):
        self.status = status
        self.reason = reason
        self.payload = payload

    def read(self):
        return json.dumps(self.payload)


class MockConnection:
    host = None
    method = None
    path = None
    params = None
    headers = None

    def __init__(self, host):
        self.host = host

    def request(self, method, path, params, headers):
        self.method = method
        self.path = path
        self.params = params
        self.headers = headers

    def getresponse(self):
        return MockResponse(200, 'OK', {'response': {'return': {'order_id': 'OID-223344'}}})

    def close(self):
        pass


if __name__ == '__main__':
    pass
