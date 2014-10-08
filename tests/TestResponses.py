#!/usr/bin/env python

import unittest
import json
from digicert.api.responses import RequestFailedResponse,\
    OrderCertificateSucceededResponse,\
    OrderViewDetailsSucceededResponse,\
    RetrieveCertificateSucceededResponse,\
    CertificateDetails,\
    PendingReissue

class TestResponses(unittest.TestCase):
    def test_failed_response(self):
        rsp = RequestFailedResponse('Not Found')
        self.assertEqual('failure', rsp.result)
        self.assertEqual(['Not Found'], rsp.error_codes)

        rsp = RequestFailedResponse(['First Bad Thing', 'Cascading Bad Thing', 'Ultimate Bad Thing'])
        self.assertEqual('failure', rsp.result)
        self.assertEqual(['First Bad Thing', 'Cascading Bad Thing', 'Ultimate Bad Thing'], rsp.error_codes)

    def test_order_certificate_succeeded_response(self):
        rsp = OrderCertificateSucceededResponse('12345')
        self.assertEqual('12345', rsp.return_obj.order_id)

    def test_order_view_details_succeeded_response(self):
        certificate_details =\
            CertificateDetails('12345',
                               'issued',
                               'SSL Plus',
                               '1 Year(s)',
                               '',
                               'fake.com',
                               '',
                               '01-FEB-2013',
                               '01-FEB-2013',
                               '01-FEB-2014',
                               '2',
                               'Apache')
        pending_reissue = PendingReissue('fake.com', 'fake.com')
        rsp = OrderViewDetailsSucceededResponse(certificate_details, pending_reissue)
        self.assertEqual('12345', rsp.return_obj.certificate_details.order_id)
        self.assertEqual('issued', rsp.return_obj.certificate_details.status)
        self.assertEqual('SSL Plus', rsp.return_obj.certificate_details.product_name)
        self.assertEqual('1 Year(s)', rsp.return_obj.certificate_details.validity)
        self.assertEqual('', rsp.return_obj.certificate_details.org_unit)
        self.assertEqual('fake.com', rsp.return_obj.certificate_details.common_name)
        self.assertEqual([], rsp.return_obj.certificate_details.sans)
        self.assertEqual('01-FEB-2013', rsp.return_obj.certificate_details.order_date)
        self.assertEqual('01-FEB-2013', rsp.return_obj.certificate_details.valid_from)
        self.assertEqual('01-FEB-2014', rsp.return_obj.certificate_details.valid_till)
        self.assertEqual(2, rsp.return_obj.certificate_details.server_type)
        self.assertEqual('Apache', rsp.return_obj.certificate_details.server_type_name)
        self.assertEqual('fake.com', rsp.return_obj.pending_reissue.common_name)
        self.assertEqual(['fake.com'], rsp.return_obj.pending_reissue.sans)

    def test_retrieve_certificate_succeeded_response(self):
        certs = {
            'certificate': 'end-entity certificate',
            'intermediate': 'intermediate certificate',
            'root': 'root certificate',
            'pkcs7': 'pkcs7 certificate'
        }
        rsp = RetrieveCertificateSucceededResponse('12345', '1A2B3C', certs)
        self.assertEqual('12345', rsp.return_obj.order_id)
        self.assertEqual('1A2B3C', rsp.return_obj.serial)
        self.assertEqual(certs, rsp.return_obj.certs)

if __name__ == '__main__':
    unittest.main()