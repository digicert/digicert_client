#!/usr/bin/env python

import unittest

from ..api.queries.v1 import DownloadCertificateQuery


class TestRetrieveCertificateQueryV1(unittest.TestCase):
    _customer_name = '12345'
    _customer_api_key = 'abapsdrtaewrh89249sbs89as0d'
    _api_host = 'www.digicert.com'
    _api_path = '/clients/retail/api/?action=retrieve_certificate'

    def test_construct(self):
        odq = DownloadCertificateQuery(customer_name=self._customer_name,
                                       customer_api_key=self._customer_api_key,
                                       order_id='567890')
        self.assertEqual(self._customer_name, odq.customer_name)
        self.assertEqual(self._customer_api_key, odq.customer_api_key)
        self.assertEqual('567890', odq.order_id)


if __name__ == '__main__':
    unittest.main()