#!/usr/bin/env python

import json
from base64 import b64encode
from urllib import urlencode

from ..https import VerifiedHTTPSConnection
from ..api.responses import RequestFailedResponse


class DigiCertApiRequest(object):
    """Base class for DigiCert Retail API requests."""

    class ApiSpecifics(object):
        def __init__(self, api_path, customer_api_key):
            self.api_path = api_path
            self.customer_api_key = customer_api_key

        def get_api_base_path(self):
            return self.api_path

        def get_authorization_header_name(self):
            raise NotImplementedError

        def get_authorization_header_value(self):
            raise NotImplementedError

    class RetailApiSpecifics(ApiSpecifics):
        def __init__(self, customer_api_key, customer_name):
            super(DigiCertApiRequest.RetailApiSpecifics, self).__init__('/clients/retail/api/', customer_api_key)
            self.customer_name = customer_name

        def get_authorization_header_name(self):
            return 'Authorization'

        def get_authorization_header_value(self):
            return b64encode(':'.join([self.customer_name, self.customer_api_key]))

    class CertCentralApiSpecifics(ApiSpecifics):
        def __init__(self, customer_api_key):
            super(DigiCertApiRequest.CertCentralApiSpecifics, self).__init__('/services/v2/', customer_api_key)

        def get_authorization_header_name(self):
            return 'X-DC-DEVKEY'

        def get_authorization_header_value(self):
            return self.customer_api_key

    response_type = 'json'
    host = 'www.digicert.com'
    _base_path = ''

    _headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}

    def __init__(self, customer_api_key, customer_name=None, **kwargs):
        """
        Base class request object constructor.

        All required parameters must be specified in the constructor positionally or by keyword.
        Optional parameters may be specified via kwargs.

        :param customer_api_key: the customer's DigiCert API key
        :param customer_name: the customer's DigiCert account number, e.g. '012345'  This parameter
        is optional.  If provided, the DigiCert Retail API will be used; if not, the DigiCert CertCentral API
        will be used.
        :param kwargs:
        :return:
        """
        for key, value in kwargs.items():
            if not self._process_special(key, value):
                setattr(self, key, value)

        if not customer_api_key:
            raise RuntimeError('No value provided for required property "customer_api_key"')

        if customer_name:
            api = DigiCertApiRequest.RetailApiSpecifics(customer_api_key, customer_name)
        else:
            api = DigiCertApiRequest.CertCentralApiSpecifics(customer_api_key)

        self.set_header(api.get_authorization_header_name(), api.get_authorization_header_value())
        self._base_path = api.get_api_base_path()

    def _process_special(self, key, value):
        pass

    def _get_method(self):
        raise NotImplementedError()

    def _get_path(self):
        raise NotImplementedError

    def _get_base_path(self):
        return self._base_path

    def _process_response(self, status, reason, response):
        if status >= 300:
            return RequestFailedResponse([{'status': status, 'reason': reason}])
        try:
            if response['response']['result'] == 'failure':
                return RequestFailedResponse(response['response']['error_codes'])
            return self._subprocess_response(status, reason, response)
        except KeyError:
            return RequestFailedResponse([{'result': 'unknown failure', 'response': str(response)}])

    def _subprocess_response(self, status, reason, response):
        raise NotImplementedError

    def get_params(self):
        """
        Retrieve the urlencoded set of parameters that will be sent
        as the payload of the command.

        :return: Urlencoded payload
        """
        return urlencode(self.__dict__)

    def set_header(self, header_name, header_value):
        """
        Update the headers to be sent with the pair provided.
        This will add this header to the list of headers if
        this header has not already been set, or overwrite the
        value already set for this header if one exists.
        You have been warned.

        :param header_name: Name of the header to set
        :param header_value: Value to set for this header
        :return:
        """
        self._headers[header_name] = header_value

    def get_headers(self):
        """
        Retrieve the dictionary of headers to be sent with the request.
        :return: Header dictionary
        """
        return self._headers

    def send(self, conn=None):
        """
        Send this command to the DigiCert Retail API.

        :param conn: Connection instance to use for sending the request. If no
        instance is provided, a VerifiedHTTPSConnection will be used with the default
        DigiCert API hostname.
        :return: Response from connection request.
        """
        if conn is None:
            conn = VerifiedHTTPSConnection(self.host)
        print self._get_method()
        print self._get_path()
        print self.get_params()
        print self.get_headers()
        conn.request(self._get_method(), self._get_path(), self.get_params(), self.get_headers())
        conn_rsp = conn.getresponse()
        response = self._process_response(conn_rsp.status, conn_rsp.reason, json.loads(conn_rsp.read()))
        conn.close()
        return response


if __name__ == '__main__':
    pass