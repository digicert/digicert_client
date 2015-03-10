import unittest

from . import MockConnection
from .. import CertificateOrder


class TestOrderCertificate(unittest.TestCase):
    v1_order_created_response = (201, 'Created', {
        'response': {
            'result': 'success',
            'return': {
                'order_id': 'OID-223344',
            },
        },
    },)
    v2_order_created_response = (201, 'Created', {
        'id': 'OID-223344',
        'requests': {'id': '288382'}
    },)
    me_response = (200, 'OK', {
        'id': '102938',
        "container": {
            'id': '987654',
        },
    },)
    my_org_response = (200, 'OK', {
        'organizations':
        [{
            'id': '564738',
            'name': 'FakeCo',
            'address': '123 Nowhere Lane',
            'address2': 'Infinitieth Floor',
            'zip': '12345',
            'city': 'Nowhere',
            'state': 'UT',
            'country': 'US',
            'unit': 'An Org',
            'container': {'id': '987654'},
            'organization_contact': {
                'first_name': 'William',
                'last_name': 'Billson',
                'email': 'bbillson@fakeco.biz',
                'telephone': '2345556789',
                'telephone_ext': '1001',
                'job_title': 'Janitor',
            },
        }, ],
    }, )
    my_domain_response = (200, 'OK', {
        'domains':
        [{
            'id': '239487',
            'name': 'fakeco.biz',
            'organization': {'id': '564738'},
            'container': {'id': '987654'},
        }, ],
    }, )
    v1order = CertificateOrder(host='localhost',
                               customer_api_key='abc123',
                               customer_name='12345',
                               conn=MockConnection('localhost',
                                                   responses={
                                                       '/clients/retail/api/?action=order_certificate': v1_order_created_response,
                                                   }))
    v2order = CertificateOrder(host='localhost',
                               customer_api_key='abc123',
                               conn=MockConnection('localhost',
                                                   responses={
                                                       '/services/v2/user/me': me_response,
                                                       '/services/v2/organization?container_id=987654': my_org_response,
                                                       '/services/v2/domain?container_id=987654': my_domain_response,
                                                       '/services/v2/order/certificate/ssl_plus': v2_order_created_response,
                                                       '/services/v2/order/certificate/ssl_multi_domain': v2_order_created_response,
                                                       '/services/v2/order/certificate/ssl_wildcard': v2_order_created_response,
                                                   }))

    requireds = \
        {
            'common_name': 'fakeco.biz',
            'certificate_type': 'sslplus',
            'validity': 3,
            'org_name': 'FakeCo',
            'org_addr1': '123 Nowhere Lane',
            'org_city': 'Nowhere',
            'org_state': 'UT',
            'org_zip': '12345',
            'org_country': 'US',
            'org_contact_firstname': 'William',
            'org_contact_lastname': 'Billson',
            'org_contact_email': 'bbillson@fakeco.biz',
            'org_contact_telephone': '2345556789',
            'csr': '---CSR---',
        }
    optionals = dict(requireds.items() +
        {
            'server_type': 2,
            'org_unit': 'An Org',
            'sans': ['www.fakeco.biz', 'login.fakeco.biz', 'api.fakeco.biz', 'intranet.fakeco.biz',],
            'org_addr2': 'Infinitieth Floor',
            'telephone': '2345556789',
            'org_contact_job_title': 'Janitor',
            'org_contact_telephone_ext': '1001',
            'custom_expiration_date': '2015-11-20',
            'comments': 'His shirt is too tight.',
            'not_a_field': 'nothing',
        }.items())

    def verify_response(self, response):
        self.assertEqual(201, response['http_status'])
        self.assertEqual('Created', response['http_reason'])
        self.assertEqual('OID-223344', response['id'])

    def test_place_v1_order_with_required_parameters(self):
        response = self.v1order.place(**self.requireds)
        self.verify_response(response)

    def test_place_v2_order_with_required_parameters(self):
        response = self.v2order.place(**self.requireds)
        self.verify_response(response)

    def test_place_v2_order_with_required_parameters_uc(self):
        self.requireds['certificate_type'] = 'sslmultidomain'
        response = self.v2order.place(**self.requireds)
        self.verify_response(response)

    def test_place_v2_order_with_required_parameters_wildcard(self):
        self.requireds['certificate_type'] = 'sslwildcard'
        self.requireds['sans'] = ['www.fakeco.biz', 'login.fakeco.biz', 'api.fakeco.biz', 'intranet.fakeco.biz']
        d = dict(self.requireds)
        response = self.v2order.place(**d)
        self.verify_response(response)

    ## test v2 order with non-matching org and non-matching domain
    def test_place_v2_order_with_non_matching_org(self):
        d = dict(self.requireds)
        d['org_name'] = 'Another Co'
        response = self.v2order.place(**d)
        self.assertEqual(404, response['status'])
        self.assertEqual('Not Found', response['reason'])
        self.assertEqual('No matching organization found', response['response'])

    def test_place_v2_order_with_non_matching_domain(self):
        d = dict(self.requireds)
        d['common_name'] = 'w3.fakeco.biz'
        response = self.v2order.place(**d)
        self.assertEqual(404, response['status'])
        self.assertEqual('Not Found', response['reason'])
        self.assertEqual('No matching domain found', response['response'])

    def test_place_v1_order_with_optional_parameters(self):
        response = self.v1order.place(**self.optionals)
        self.verify_response(response)

    def test_place_v2_order_with_optional_parameters(self):
        response = self.v2order.place(**self.optionals)
        self.verify_response(response)

    def test_place_v1_order_with_missing_parameters(self):
        d = dict(self.requireds)
        del d['validity']
        try:
            self.v1order.place(**d)
            self.fail('Expected exception but none thrown')
        except KeyError:
            pass

    def test_place_v2_order_with_missing_parameters(self):
        d = dict(self.requireds)
        del d['csr']
        try:
            self.v2order.place(**d)
            self.fail('Expected exception but none thrown')
        except KeyError:
            pass


if __name__ == '__main__':
    unittest.main()