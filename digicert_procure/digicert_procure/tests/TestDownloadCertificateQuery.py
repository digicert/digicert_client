#!/usr/bin/env python

import unittest

from ..api.queries.v1 import DownloadCertificateQuery as DownloadCertificateQueryV1
from ..api.queries.v2 import DownloadCertificateQuery as DownloadCertificateQueryV2


class TestDownloadCertificateQuery(object):
    _customer_name = '12345'
    _customer_api_key = 'abapsdrtaewrh89249sbs89as0d'
    _api_host = 'www.digicert.com'
    _api_path = '/clients/retail/api/?action=retrieve_certificate'

    def get_dcq(self):
        raise NotImplementedError

    def verify_dcq(self, dcq):
        self.assertEqual(self._customer_api_key, dcq.customer_api_key)
        self.assertEqual('567890', dcq.order_id)

    def test_construct(self):
        dcq = self.get_dcq()
        self.verify_dcq(dcq)


class TestDownloadCertificateQueryV1(TestDownloadCertificateQuery, unittest.TestCase):
    def get_dcq(self):
        return DownloadCertificateQueryV1(customer_name=self._customer_name,
                                          customer_api_key=self._customer_api_key,
                                          order_id='567890')

    def verify_dcq(self, dcq):
        super(TestDownloadCertificateQueryV1, self).verify_dcq(dcq)
        self.assertEqual(self._customer_name, dcq.customer_name)


class TestDownloadCertificateQueryV2(TestDownloadCertificateQuery, unittest.TestCase):
    def get_dcq(self):
        return DownloadCertificateQueryV2(customer_api_key=self._customer_api_key,
                                          order_id='567890')


if __name__ == '__main__':
    unittest.main()