#!/usr/bin/env python

import unittest
from digicert.api.queries import RetrieveCertificateQuery


class TestRetrieveCertificateQuery(unittest.TestCase):
    _customer_name = '12345'
    _customer_api_key = 'abapsdrtaewrh89249sbs89as0d'
    _api_host = 'www.digicert.com'
    _api_path = '/clients/retail/api/'

    def test_construct(self):
        odq = RetrieveCertificateQuery(self._customer_name, self._customer_api_key, '567890')
        self.assertEqual(self._customer_name, odq.customer_name)
        self.assertEqual(self._customer_api_key, odq.customer_api_key)
        self.assertEqual(self._api_host, odq._digicert_api_host)
        self.assertEqual(self._api_path, odq._digicert_api_path)
        self.assertEqual('567890', odq.order_id)


if __name__ == '__main__':
    unittest.main()