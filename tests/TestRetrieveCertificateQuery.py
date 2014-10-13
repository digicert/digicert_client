#!/usr/bin/env python

import unittest
from digicert.api.queries import RetrieveCertificateQuery
from tests import MockConnection


class TestRetrieveCertificateQuery(unittest.TestCase):
    _customer_name = '12345'
    _customer_api_key = 'abapsdrtaewrh89249sbs89as0d'
    _api_host = 'www.digicert.com'
    _api_path = '/clients/retail/api/?action=retrieve_certificate'

    def test_construct(self):
        odq = RetrieveCertificateQuery(self._customer_name, self._customer_api_key, '567890')
        self.assertEqual(self._customer_name, odq.customer_name)
        self.assertEqual(self._customer_api_key, odq.customer_api_key)
        self.assertEqual(self._api_host, odq.host)
        self.assertEqual(self._api_path.split('?')[0], odq._digicert_api_path)
        self.assertEqual('567890', odq.order_id)

    def test_send(self):
        rcq = RetrieveCertificateQuery(self._customer_name, self._customer_api_key, '567890')
        mc = MockConnection(self._api_host)
        rcq.send(conn=mc)
        self.assertEqual(self._api_host, mc.host)
        self.assertEqual(self._api_path, mc.path)
        self.assertEqual('POST', mc.method)
        self.assertEqual(rcq.get_params(), mc.params)
        self.assertEqual(rcq.get_headers(), mc.headers)


if __name__ == '__main__':
    unittest.main()