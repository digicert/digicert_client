#!/usr/bin/env python

import unittest

from ..api.queries import OrderDetailsQuery
from . import MockConnection


class TestOrderDetailsQuery(unittest.TestCase):
    _customer_name = '12345'
    _customer_api_key = 'abapsdrtaewrh89249sbs89as0d'
    _api_host = 'www.digicert.com'
    _api_path = '/clients/retail/api/?action=order_view_details'

    def test_construct(self):
        odq = OrderDetailsQuery(self._customer_name, self._customer_api_key, '567890')
        self.assertEqual(self._customer_name, odq.customer_name)
        self.assertEqual(self._customer_api_key, odq.customer_api_key)
        self.assertEqual(self._api_host, odq.host)
        self.assertEqual(self._api_path.split('?')[0], odq._digicert_api_path)
        self.assertEqual('567890', odq.order_id)

    def test_send(self):
        odq = OrderDetailsQuery(self._customer_name, self._customer_api_key, '567890')
        mc = MockConnection(self._api_host)
        odq.send(conn=mc)
        self.assertEqual(self._api_host, mc.host)
        self.assertEqual(self._api_path, mc.path)
        self.assertEqual('POST', mc.method)
        self.assertEqual(odq.get_params(), mc.params)
        self.assertEqual(odq.get_headers(), mc.headers)


if __name__ == '__main__':
    unittest.main()