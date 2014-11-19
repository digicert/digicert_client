import unittest

from .. import CertificateOrder
from . import MockConnection


class TestViewOrder(unittest.TestCase):
    v1_view_order_response = (200, 'OK', {
        'response': {
            'result': 'success',
            'return': {
                'certificate_details': {
                    'order_id': 'OID-223344',
                    'status': 'issued',
                    'product_name': 'SSL Plus',
                    'validity': '1 Year(s)',
                    'org_unit': 'FakeCo',
                    'common_name': 'fakeco.biz',
                    'sans': [
                        'www.fakeco.biz',
                        'www.fake.co.uk'
                    ],
                    'order_date': '2014-08-18T18:16:07+00:00',
                    'valid_from': '2014-08-19T18:16:07+00:00',
                    'valid_till': '2015-08-19T18:16:07+00:00',
                    'server_type': 2,
                    'server_type_name': 'Apache'
                },
                'pending_reissue': {
                    'common_name': 'fakeco.biz',
                    'sans': [
                        'api.fakeco.biz',
                        'intranet.fakeco.biz'
                    ]
                }
            }
        }
    })
    v2_view_order_response = (200, 'OK', {
        'id': 'OID-223344',
        'certificate': {
            'id': 112358,
            'thumbprint': '7D236B54D19D5EACF0881FAF24D51DFE5D23E945',
            'serial_number': '0669D46CAE79EF684A69777490602485',
            'common_name': 'fakeco.biz',
            'dns_names': [
                'www.fakeco.biz',
                'www.fake.co.uk',
            ],
            'date_created': '2014-08-19T18:16:07+00:00',
            'csr': '------fakecsr-----',
            'organization': {
                'id': 117483
            },
            'organization_units': [
                'FakeCo'
            ],
            'server_platform': {
                'id': 2,
                'name': 'Apache',
                'install_url': 'http:\/\/www.digicert.com\/ssl-certificate-installation-nginx.htm',
                'csr_url': 'http:\/\/www.digicert.com\/csr-creation-nginx.htm'
            },
            'signature_hash': 'sha256',
            'ca_cert': {
                'id': 'f7slk4shv9s2wr3',
                'name': 'DCert Private CA'
            }
        },
        'status': 'issued',
        'date_created': '2014-08-19T18:16:07+00:00',
        'organization': {
            'name': 'Fake Co',
            'city': 'Nowhere',
            'state': 'UT',
            'country': 'US'
        },
        'auto_renew': 10,
        'container': {
            'id': 5,
            'name': 'A Container'
        },
        'product': {
            'name_id': 'ssl_plus',
            'name': 'SSL Plus',
            'type': 'ssl_certificate'
        },
        'organization_contact': {
            'first_name': 'William',
            'last_name': 'Billson',
            'email': 'bbillson@fakeco.biz',
            'telephone': '2345556789'
        },
        'technical_contact': {
            'first_name': 'William',
            'last_name': 'Billson',
            'email': 'bbillson@fakeco.biz',
            'telephone': '2345556789'
        },
        'user': {
            'id': 153208,
            'first_name': 'Robert',
            'last_name': 'Bobson',
            'email': 'bbobson@fakeco.biz'
        },
        'requests': [{
            'id': 1
        }]
    })
    v1order = CertificateOrder(host='localhost',
                               customer_api_key='abc123',
                               customer_name='12345',
                               conn=MockConnection('localhost',
                                                   responses={
                                                       '/clients/retail/api/?action=order_view_details': v1_view_order_response,
                                                   }))
    v2order = CertificateOrder(host='localhost',
                               customer_api_key='abc123',
                               conn=MockConnection('localhost',
                                                   responses={
                                                       '/services/v2/order/certificate/OID-223344': v2_view_order_response,
                                                   }))
    order_kwargs = {'order_id': 'OID-223344'}

    def verify_response(self, response):
        self.assertEquals(200, response['http_status'])
        self.assertEquals('OK', response['http_reason'])
        self.assertEquals('fakeco.biz', response['certificate']['common_name'])
        self.assertEquals('2014-08-19T18:16:07+00:00', response['certificate']['date_created'])
        self.assertEquals('www.fakeco.biz', response['certificate']['dns_names'][0])
        self.assertEquals('www.fake.co.uk', response['certificate']['dns_names'][1])
        self.assertEquals('FakeCo', response['certificate']['organization_units'][0])
        self.assertEquals(2, response['certificate']['server_platform']['id'])
        self.assertEquals('Apache', response['certificate']['server_platform']['name'])
        self.assertEquals('SSL Plus', response['product']['name'])

    def test_view_v1_order(self):
        response = self.v1order.view(**self.order_kwargs)
        self.verify_response(response)

    def test_view_v2_order(self):
        response = self.v2order.view(**self.order_kwargs)
        self.verify_response(response)

    def test_view_v1_order_without_order_id(self):
        d = {'not_order_id': 'hi'}
        try:
            self.v1order.view(**d)
            self.fail('Expected exception but none caught')
        except KeyError:
            pass

    def test_view_v2_order_without_order_id(self):
        d = {'not_order_id': 'hi'}
        try:
            self.v2order.view(**d)
            self.fail('Expected exception but none caught')
        except KeyError:
            pass


if __name__ == '__main__':
    unittest.main()