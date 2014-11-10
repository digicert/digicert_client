#!/usr/bin/env python

from ...api import DigiCertProcureRequest
from ...api.responses import OrderCertificateSucceededResponse


class DigiCertProcureCommand(DigiCertProcureRequest):
    """Base class for CQRS-style Command objects."""

    def __init__(self, customer_api_key, customer_name=None, **kwargs):
        """
        RetailApiCommand constructor

        :param customer_api_key: the customer's DigiCert API key
        :param customer_name: the customer's DigiCert account number, e.g. '012345'  This parameter
        is optional.  If provided, the DigiCert Retail API will be used; if not, the DigiCert CertCentral API
        will be used.
        :param kwargs:
        :return:
        """
        super(DigiCertProcureCommand, self).__init__(customer_name, customer_api_key, **kwargs)

    def _get_method(self):
        return 'POST'

    def _process_special(self, key, value):
        raise NotImplementedError()


class OrderCertificateCommand(DigiCertProcureCommand):
    """CQRS-style Command object for ordering a new certificate."""

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
        """Contains supported values for the 'certificate_type' property of OrderCertificateCommand."""

        SSLPLUS = 'sslplus'
        UC = 'uc'
        WILDCARD = 'wildcard'
        EVSSL = 'evssl'
        EVMULTI = 'evmulti'

        def __iter__(self):
            for certtype in [self.SSLPLUS, self.UC, self.WILDCARD, self.EVSSL, self.EVMULTI, ]:
                yield certtype

    class Validity(object):
        """Contains supported values for the 'validity' property of OrderCertificateCommand."""
        ONE_YEAR = 1
        TWO_YEARS = 2
        THREE_YEARS = 3

        def __iter__(self):
            for period in [self.ONE_YEAR, self.TWO_YEARS, self.THREE_YEARS, ]:
                yield period


    def __init__(self,
                 customer_api_key,
                 certificate_type,
                 csr,
                 validity,
                 common_name,
                 org,
                 customer_name=None,
                 **kwargs):
        """
        Constructs an OrderCertificateCommand, a CQRS-style Command object for ordering certificates.

        All required parameters must be specified in the constructor positionally or by keyword.
        Optional parameters may be specified via kwargs.

        :param customer_api_key: the customer's DigiCert API key
        :param certificate_type: type of certificate being ordered (see OrderCertificateCommand.CertificateType)
        :param csr: Base64-encoded text of the certificate signing request for this certificate
        :param validity: years of validity for this certificate (see OrderCertificateCommand.Validity)
        :param common_name: the name to be secured in the certificate, e.g. example.com
        :param org: the organization which owns the certificate
        :param customer_name: the customer's DigiCert account number, e.g. '012345'  This parameter
        is optional.  If provided, the DigiCert Retail API will be used; if not, the DigiCert CertCentral API
        will be used.
        :param kwargs:
        :return:
        """
        super(OrderCertificateCommand, self).__init__(customer_api_key, customer_name, **kwargs)
        self.certificate_type = certificate_type
        self.csr = csr
        self.validity = int(validity)
        self.common_name = common_name
        self.org_name = org.name
        self.org_addr1 = org.addr.addr1
        if hasattr(org.addr, 'addr2'):
            self.org_addr2 = org.addr.addr2
        self.org_city = org.addr.city
        self.org_state = org.addr.state
        self.org_zip = org.addr.zip
        self.org_country = org.addr.country
        if hasattr(org.addr, 'telephone'):
            self.telephone = org.addr.telephone
        self.org_contact_firstname = org.contact.firstname
        self.org_contact_lastname = org.contact.lastname
        self.org_contact_email = org.contact.email
        self.org_contact_telephone = org.contact.telephone
        if hasattr(org.contact, 'job_title'):
            self.org_contact_job_title = org.contact.job_title
        if hasattr(org.contact, 'telephone_ext'):
            self.org_contact_telephone_ext = org.contact.telephone_ext

        for field in ['certificate_type', 'csr', 'validity', 'common_name',
                      'org_name', 'org_addr1', 'org_city', 'org_state', 'org_zip', 'org_country',
                      'org_contact_firstname', 'org_contact_lastname', 'org_contact_email', 'org_contact_telephone']:
            if not field in self.__dict__:
                raise RuntimeError('No value provided for required property "%s"' % field)

    def _get_path(self):
        return '%s?action=order_certificate' % self._get_base_path()

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