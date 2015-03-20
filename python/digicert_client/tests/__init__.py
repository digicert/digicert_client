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
    responses = None
    method = None
    path = None
    params = None
    headers = None

    def __init__(self, host, responses=None):
        self.host = host
        self.responses = responses

    def request(self, method, path, params, headers):
        self.method = method
        self.path = path
        self.params = params
        self.headers = headers

    def getresponse(self):
        if self.responses and self.path in self.responses:
            status, reason, response = self.responses[self.path]
        else:
            status = 200
            reason = 'OK'
            response = {'response': {'result': 'success', 'return': {'order_id': 'OID-223344'}}}
        return MockResponse(status, reason, response)

    def close(self):
        pass


if __name__ == '__main__':
    pass
