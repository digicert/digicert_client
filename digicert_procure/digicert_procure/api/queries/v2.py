from ..queries import Query


class OrderDetailsQuery(Query):
    def __init__(self, customer_api_key, **kwargs):
        super(OrderDetailsQuery, self).__init__(customer_api_key, customer_name=None, **kwargs)


class RetrieveCertificateQuery(Query):
    def __init__(self, customer_api_key, **kwargs):
        super(RetrieveCertificateQuery, self).__init__(customer_api_key, customer_name=None, **kwargs)


if __name__ == '__main__':
    pass