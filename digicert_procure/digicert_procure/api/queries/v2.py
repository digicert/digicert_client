from ..queries import Query
from ..responses.v2 import User


class V2Query(Query):
    _base_path = '/services/v2'

    def __init__(self, customer_api_key, **kwargs):
        super(V2Query, self).__init__(customer_api_key=customer_api_key, customer_name=None, **kwargs)
        self.set_header('X-DC-DEVKEY', customer_api_key)

    def get_method(self):
        return 'GET'

    def _is_failure_response(self, response):
        return 'errors' in response


class OrderDetailsQuery(V2Query):
    def __init__(self, customer_api_key, **kwargs):
        super(OrderDetailsQuery, self).__init__(customer_api_key=customer_api_key, **kwargs)


class RetrieveCertificateQuery(V2Query):
    def __init__(self, customer_api_key, **kwargs):
        super(RetrieveCertificateQuery, self).__init__(customer_api_key=customer_api_key, **kwargs)


class MyUserQuery(V2Query):
    def __init__(self, customer_api_key):
        super(MyUserQuery, self).__init__(customer_api_key=customer_api_key)

    def get_path(self):
        return '%s/user/me' % self._base_path

    def _subprocess_response(self, status, reason, response):
        return User(**response)


if __name__ == '__main__':
    pass