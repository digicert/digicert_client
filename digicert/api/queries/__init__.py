#!/usr/bin/env python

from digicert.api import RetailApiRequest


class RetailApiQuery(RetailApiRequest):
    def __init__(self, customer_name, customer_api_key, **kwargs):
        RetailApiRequest.__init__(self, customer_name, customer_api_key, **kwargs)

    def _get_method(self):
        return 'GET'


class OrderDetailsQuery(RetailApiQuery):
    order_id = None

    def __init__(self, customer_name, customer_api_key, order_id, **kwargs):
        RetailApiQuery.__init__(self, customer_name, customer_api_key, **kwargs)
        self.order_id = order_id


class RetrieveCertificateQuery(RetailApiQuery):
    order_id = None

    def __init__(self, customer_name, customer_api_key, order_id, **kwargs):
        RetailApiQuery.__init__(self, customer_name, customer_api_key, **kwargs);
        self.order_id = order_id


if __name__ == '__main__':
    pass