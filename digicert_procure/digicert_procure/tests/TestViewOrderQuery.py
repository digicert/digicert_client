#!/usr/bin/env python

import unittest

from ..api.queries.v1 import ViewOrderDetailsQuery as ViewOrderDetailsQueryV1
from ..api.queries.v2 import ViewOrderDetailsQuery as ViewOrderDetailsQueryV2


class BaseTestViewOrderQuery(object):
    _customer_name = '12345'
    _customer_api_key = 'abapsdrtaewrh89249sbs89as0d'
    _api_host = 'www.digicert.com'
    _api_path = '/clients/retail/api/?action=order_view_details'

    def get_odq(self):
        raise NotImplementedError

    def verify_odq(self, odq):
        self.assertEqual(self._customer_api_key, odq.customer_api_key)
        self.assertEqual('567890', odq.order_id)

    def test_construct(self):
        odq = self.get_odq()
        self.verify_odq(odq)


class TestViewOrderQueryV1(BaseTestViewOrderQuery, unittest.TestCase):
    def get_odq(self):
        return ViewOrderDetailsQueryV1(customer_name=self._customer_name,
                                       customer_api_key=self._customer_api_key,
                                       order_id='567890')

    def verify_odq(self, odq):
        super(TestViewOrderQueryV1, self).verify_odq(odq)
        self.assertEqual(self._customer_name, odq.customer_name)


class TestViewOrderQueryV2(BaseTestViewOrderQuery, unittest.TestCase):
    def get_odq(self):
        return ViewOrderDetailsQueryV2(customer_api_key=self._customer_api_key,
                                       order_id='567890')


if __name__ == '__main__':
    unittest.main()