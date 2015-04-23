#!/usr/bin/env python

import json
from urllib import urlencode

from ..https import VerifiedHTTPSConnection


class Request(object):
    """
    Abstraction of a REST request.  A Request object uses the provided
    connection to issue the request represented by the provided action
    to the provided host.  The action and host are provided via the constructor;
    the connection is also optionally provided via the constructor.
    """

    def __init__(self, action, host, conn=None):
        """
        Constructs a Request with the provided Action, host, and connection.
        Connection is optional but assumes the same interface as HTTPConnection.
        If not provided, the default connection is of type VerifiedHTTPSConnection
        which is a subclass of HTTPSConnection that also performs peer verification.

        :param action:  The Action to initiate.  Probably a subclass of Action.
        :param host:  The host to send the request to.
        :param conn:  The optional HTTPConnection-style connection to use, defaults
        to VerifiedHTTPSConnection.
        """
        self.action = action
        self.host = host
        self.conn = conn if conn is not None else VerifiedHTTPSConnection(host)

    def send(self):
        """
        Issues the request represented by this object, obtains the response, extracts the
        response data (converting it from JSON if it is in JSON format), sends all the
        response data to the Action object for processing, and returns the result of the
        response processing.
        """
        self.conn.request(self.action.get_method(),
                          self.action.get_path(),
                          self.action.get_params(),
                          self.action.get_headers())
        conn_rsp = self.conn.getresponse()
        response_data = conn_rsp.read()
        try:
            payload = json.loads(response_data)
        except ValueError:
            payload = response_data
        response = self.action.process_response(conn_rsp.status, conn_rsp.reason, payload)
        self.conn.close()
        return response


class Action(object):
    """
    Base class for all Commands or Queries.
    """
    _headers = {'Accept': 'application/json'}

    def __init__(self, customer_api_key, customer_name=None, **kwargs):
        """
        Constructor for an Action.

        :param customer_api_key: the customer's DigiCert API key
        :param customer_name: the customer's DigiCert account number, e.g. '012345'  Required for
        V1-style actions, not required for V2-style actions.
        :param kwargs:
        :return:
        """
        self._customer_api_key = customer_api_key
        if customer_name is not None:
            self._customer_name = customer_name
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

    def _make_response(self, status, reason, response):
        if len(response) == 0:
            return dict({'http_status': status, 'http_reason': reason}.items())
        else:
            return dict({'http_status': status, 'http_reason': reason}.items() + response.items())

    def process_response(self, status, reason, response):
        if status >= 300:
            return self._make_response(status, reason, response)
        try:
            return self._subprocess_response(status, reason, response)
        except KeyError:
            return self._make_response(status, reason, {'result': 'unknown failure', 'response': str(response)})


if __name__ == '__main__':
    pass
