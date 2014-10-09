#!/usr/bin/env python

from digicert.api import RetailApiRequest
from digicert.api.responses import OrderCertificateSucceededResponse, RequestFailedResponse


class RetailApiCommand(RetailApiRequest):
    def __init__(self, customer_name, customer_api_key, **kwargs):
        super(RetailApiCommand, self).__init__(customer_name, customer_api_key, **kwargs)

    def _get_method(self):
        return 'POST'

    def _process_special(self, key, value):
        raise NotImplementedError()


class OrderCertificateCommand(RetailApiCommand):
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

    class CertificateType(object):
        SSLPLUS = 'sslplus'
        UC = 'uc'
        WILDCARD = 'wildcard'
        EVSSL = 'evssl'
        EVMULTI = 'evmulti'

    class Validity(object):
        ONE_YEAR = 1
        TWO_YEARS = 2
        THREE_YEARS = 3

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
        super(OrderCertificateCommand, self).__init__(customer_name, customer_api_key, **kwargs)
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

        for field in ['certificate_type', 'csr', 'validity', 'common_name',
                      'org_name', 'org_addr1', 'org_city', 'org_state', 'org_zip', 'org_country',
                      'org_contact_firstname', 'org_contact_lastname', 'org_contact_email', 'org_contact_telephone']:
            if not field in self.__dict__:
                raise RuntimeError('No value provided for required property "%s"' % field)

    def _get_path(self):
        return '%s?action=order_certificate' % self._digicert_api_path

    def _process_special(self, key, value):
        if 'server_type' == key:
            self.server_type = int(value)
            return True
        return False

    def _subprocess_response(self, status, reason, response):
        order_id = None
        try:
            order_id = response['response']['return']['order_id']
        except KeyError:
            pass
        return OrderCertificateSucceededResponse(status, reason, order_id)


if __name__ == '__main__':
    pass