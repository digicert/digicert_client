import unittest

from . import MockConnection
from .. import CertificateOrder


class TestDownloadCertificate(unittest.TestCase):
    cert = '-----BEGIN CERTIFICATE-----\r\n' + \
        'MIIFLzCCBBegAwIBAgIQDrB5sV1kcdaaq0JZlUyGMTANBgkqhkiG9w0BAQsFADBT\r\n' + \
        'I3gCIROT/MrrhQrVs6QbIxOGUIxhXs3FaZDcJVM46R8NUVI=\r\n' + \
        '-----END CERTIFICATE-----\r\n'
    inter = '-----BEGIN CERTIFICATE-----\r\n' + \
        'MIIEtTCCA52gAwIBAgIQDIu2tdNzzmdKCjRKdwemlzANBgkqhkiG9w0BAQsFADBn\r\n' + \
        'am8+4SqHrmoq\r\n' + \
        '-----END CERTIFICATE-----\r\n'
    root = '-----BEGIN CERTIFICATE-----\r\n' + \
        'MIIDuzCCAqOgAwIBAgIQD2u/YBwj+V0fclDibEkALjANBgkqhkiG9w0BAQUFADBn\r\n' + \
        'ORWAxdScvkQdqON/Mlcstd/j8biZXvO2doaxo+zsVM94BKqdMnqnhRWh/9m/fEE=\r\n' + \
        '-----END CERTIFICATE-----\r\n'
    pkcs7 = '-----BEGIN PKCS7-----\r\n' + \
        'MIIOGQYJKoZIhvcNAQcCoIIOCjCCDgYCAQExADALBgkqhkiG9w0BBwGggg3uMIIF\r\n' + \
        '7gN6zBBxQCfQuMxAA==\r\n' + \
        '-----END PKCS7-----\r\n'
    cert_id = '990929'
    v1_download_order_response = (200, 'OK', {
        'response': {
            'result': 'success',
            'return': {
                'order_id': 'OID-223344',
                'serial': '07C2EDE40FEEA2AA03C0615F32D3A26D',
                'certs': {
                    'certificate': cert,
                    'intermediate': inter,
                    'root': root,
                    'pkcs7': pkcs7
                }
            }
        }
    })
    v2_view_order_response = (200, 'OK', {'certificate': {'id': '990929'}})
    v2_download_order_response = (200, 'OK', '%s%s%s' % (cert, inter, root))
    v1_order = CertificateOrder(host='localhost',
                               customer_api_key='abc123',
                               customer_name='12345',
                               conn=MockConnection('localhost',
                                                   responses={
                                                       '/clients/retail/api/?action=retrieve_certificate': v1_download_order_response,
                                                   }))
    v2_order = CertificateOrder(host='localhost',
                               customer_api_key='abc123',
                               conn=MockConnection('localhost',
                                                   responses={
                                                       '/services/v2/order/certificate/OID-223344': v2_view_order_response,
                                                       '/services/v2/certificate/990929/download/format/pem_all': v2_download_order_response,
                                                   }))

    def verify_response(self, response):
        self.assertEqual(200, response['http_status'])
        self.assertEqual('OK', response['http_reason'])
        self.assertEqual(self.cert.strip(), response['certificates']['certificate'])
        self.assertEqual(self.inter.strip(), response['certificates']['intermediate'])
        self.assertEqual(self.root.strip(), response['certificates']['root'])
        if 'pkcs7' in response['certificates']:
            self.assertEqual(self.pkcs7.strip(), response['certificates']['pkcs7'])

    def test_download_v1_order(self):
        response = self.v1_order.download(**{'order_id': 'OID-223344'})
        self.verify_response(response)

    def test_download_v2_order(self):
        response = self.v2_order.download(**{'order_id': 'OID-223344'})
        self.verify_response(response)

    def test_download_v2_order_with_order_id_param(self):
        response = self.v2_order.download(digicert_order_id='OID-223344')
        self.verify_response(response)

    def test_download_v1_order_with_certificate_id_fails(self):
        try:
            self.v1_order.download(**{'certificate_id': self.cert_id})
            self.fail('Expected exception but none thrown')
        except KeyError:
            pass

    def test_download_v2_order_with_certificate_id(self):
        response = self.v2_order.download(**{'certificate_id': self.cert_id})
        self.verify_response(response)

    def test_download_v2_order_with_certificate_id_param(self):
        response = self.v2_order.download(digicert_certificate_id=self.cert_id)
        self.verify_response(response)

    def test_download_v1_order_without_order_id(self):
        try:
            self.v1_order.download(**{'not_order_id': 'fake'})
            self.fail('Expected exception but none thrown')
        except KeyError:
            pass

    def test_download_v2_order_without_order_id(self):
        try:
            self.v2_order.download(**{'not_order_id': 'fake'})
            self.fail('Expected exception but none thrown')
        except KeyError:
            pass


if __name__ == '__main__':
    unittest.main()