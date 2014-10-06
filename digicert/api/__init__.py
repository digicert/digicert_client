#!/usr/bin/env python

from base64 import b64encode
from urllib import urlencode
from httplib import HTTPSConnection


class RetailApiRequest:
    customer_name = None
    customer_api_key = None
    response_type = 'json'

    _digicert_api_host = 'www.digicert.com'
    _digicert_api_path = '/clients/retail/api/'

    _headers = {'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'}

    def __init__(self, customer_name, customer_api_key, **kwargs):
        self.customer_name = customer_name
        self.customer_api_key = customer_api_key
        for key, value in kwargs.items():
            if not self._process_special(key, value):
                setattr(self, key, value)
        self.set_header('Authorization', self.get_authorization())

    def _process_special(self, key, value):
        raise NotImplementedError()

    def _get_method(self):
        raise NotImplementedError()

    def get_authorization(self):
        """
        Retrieve the encoded authorization header value that is expected
        by the Retail API.
        :return: Authorization value
        """
        return b64encode(':'.join([self.customer_name, self.customer_api_key]))

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
        Take care my child.
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
        instance is provided, an HTTPSConnection will be used with the default
        DigiCert API hostname.
        :return: Response from connection request.
        """
        if conn is None:
            conn = HTTPSConnection(self._digicert_api_host)
        conn.request(self._get_method(), self._digicert_api_path, self.get_params(), self.get_headers())
        response = conn.getresponse()
        conn.close()
        return response


if __name__ == '__main__':
    pass