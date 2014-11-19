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
        return False

    def get_path(self):
        return '/services/v2/order/certificate/%s' % self._get_cert_type()

    def _get_cert_type(self):
        v1_cert_type_to_v2_cert_type = {'sslplus': 'ssl_plus'}
        if self.certificate_type in v1_cert_type_to_v2_cert_type:
            return v1_cert_type_to_v2_cert_type[self.certificate_type]
        return self.certificate_type

    def __str__(self):
        return json.dumps(self.__dict__, indent=2, separators=(',', ': '))

    def _subprocess_response(self, status, reason, response):
        return self._make_response(status, reason, response)

if __name__ == '__main__':
    pass
