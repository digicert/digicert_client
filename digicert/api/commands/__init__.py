#!/usr/bin/env python

from base64 import b64encode
from urllib import urlencode
from httplib import HTTPSConnection


class RetailCommand:
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
        pass

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
        conn.request('POST', self._digicert_api_path, self.get_params(), self.get_headers())
        response = conn.getresponse()
        conn.close()
        return response


class OrderCertificateCommand(RetailCommand):
    certificate_type = None
    csr = None
    validity = None
    server_type = -1
    org_unit = None
    common_name = None
    sans = None
    org_name = None
    org_addr1 = None
    org_addr2 = None
    org_city = None
    org_state = None
    org_zip = None
    org_country = None
    telephone = None
    org_contact_job_title = None
    org_contact_firstname = None
    org_contact_lastname = None
    org_contact_email = None
    org_contact_telephone = None
    org_contact_telephone_ext = None

    def __init__(self,
                 customer_name,
                 customer_api_key,
                 certificate_type,
                 csr,
                 validity,
                 common_name,
                 org_name,
                 org_addr1,
                 org_city,
                 org_state,
                 org_zip,
                 org_country,
                 org_contact_firstname,
                 org_contact_lastname,
                 org_contact_email,
                 org_contact_telephone,
                 **kwargs):
        RetailCommand.__init__(self, customer_name, customer_api_key, **kwargs)
        self.certificate_type = certificate_type
        self.csr = csr
        self.validity = int(validity)
        self.common_name = common_name
        self.org_name = org_name
        self.org_addr1 = org_addr1
        self.org_city = org_city
        self.org_state = org_state
        self.org_zip = org_zip
        self.org_country = org_country
        self.org_contact_firstname = org_contact_firstname
        self.org_contact_lastname = org_contact_lastname
        self.org_contact_email = org_contact_email
        self.org_contact_telephone = org_contact_telephone

    def _process_special(self, key, value):
        if 'server_type' == key:
            self.server_type = int(value)
            return True
        return False


if __name__ == '__main__':
    pass