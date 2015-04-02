import json

from . import Command


class V2Command(Command):
    def __init__(self, customer_api_key, **kwargs):
        super(V2Command, self).__init__(customer_api_key=customer_api_key, customer_name=None, **kwargs)
        self.set_header('X-DC-DEVKEY', customer_api_key)
        self.set_header('Content-Type', 'application/json')

    def _is_failure_response(self, response):
        return 'errors' in response

    def get_params(self):
        return json.dumps(self.__dict__)


class OrderCertificateCommand(V2Command):
    def __init__(self, customer_api_key, **kwargs):
        """
        Constructs an OrderCertificateCommand, a CQRS-style Command object for ordering certificates.
        This is for ordering certificates through DigiCert's V2 API.

        :param customer_api_key: the customer's DigiCert API key
        :param kwargs:  The following properties should be included in the kwargs:
          - certificate_type
          - csr
          - validity
          - common_name
          - org_name
          - org_addr1
          - org_city
          - org_state (2-character code - US state, Canadian Province, etc.)
          - org_zip
          - org_country (2-character code)
          - org_contact_firstname
          - org_contact_lastname
          - org_contact_email
          - org_contact_telephone

          Supported optional properties include:
          - server_type
          - org_unit
          - sans (array of strings)
          - org_addr2
          - telephone
          - org_contact_job_title
          - org_contact_telephone_ext
          - custom_expiration_date
          - comments

        :return:
        """
        super(OrderCertificateCommand, self).__init__(customer_api_key=customer_api_key, **kwargs)
        self.certificate =\
            {
                'common_name': kwargs['common_name'],
                'csr': kwargs['csr'],
                'organization_units': [] if not 'organization_units' in kwargs else kwargs['organization_units'],
                'server_platform': {'id': -1} if not 'server_platform' in kwargs else {'id': kwargs['server_platform']},
                'signature_hash': 'sha256' if not 'signature_hash' in kwargs else kwargs['signature_hash'],
            }
        self.organization = {'id': kwargs['organization_id']}
        self.validity_years = kwargs['validity']

    def _process_special(self, key, value):
        if 'server_type' == key:
            self.server_type = int(value)
            return True
        elif 'validity' == key:
            self.validity = int(value)
            return True
        return False

    def get_path(self):
        return '/services/v2/order/certificate/%s' % self._get_cert_type()

    def _get_cert_type(self):
        v1_cert_type_to_v2_cert_type = {'sslplus': 'ssl_plus', 'sslmultidomain': 'ssl_multi_domain', 'sslwildcard': 'ssl_wildcard', 'sslevplus': 'ssl_ev_plus', 'sslevmultidomain': 'ssl_ev_multi_domain'}
        # SSLPLUS = 'sslplus' UC = 'uc' WILDCARD = 'wildcard' EVSSL = 'evssl' EVMULTI = 'evmulti'
        if self.certificate_type in v1_cert_type_to_v2_cert_type:
            return v1_cert_type_to_v2_cert_type[self.certificate_type]
        return self.certificate_type

    def __str__(self):
        return json.dumps(self.__dict__, indent=2, separators=(',', ': '))

    def _subprocess_response(self, status, reason, response):
        return self._make_response(status, reason, response)


class UploadCSRCommand(V2Command):

    def __init__(self, customer_api_key, **kwargs):
        """
        Constructs an OrderCertificateCommand, a CQRS-style Command object for ordering certificates.
        This is for ordering certificates through DigiCert's V2 API.

        :param customer_api_key: the customer's DigiCert API key
        :param kwargs:  The following properties should be included in the kwargs:
          - order_id
          - csr

        :return:
        """
        super(UploadCSRCommand, self).__init__(customer_api_key=customer_api_key, **kwargs)
        self.order_id = kwargs['order_id']

    def get_path(self):
        return '/services/v2/order/certificate/%s/csr' % self.order_id

    def _subprocess_response(self, status, reason, response):
        return self._make_response(status, reason, response)


if __name__ == '__main__':
    pass
