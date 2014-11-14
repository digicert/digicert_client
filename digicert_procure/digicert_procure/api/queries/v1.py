from base64 import b64encode

from ..queries import Query
from ..responses import OrderViewDetailsSucceededResponse,\
    RetrieveCertificateSucceededResponse,\
    CertificateDetails,\
    PendingReissue,\
    RetrievedCertificate


class V1Query(Query):
    def __init__(self, customer_api_key, customer_name, **kwargs):
        super(V1Query, self).__init__(customer_api_key, customer_name=customer_name, **kwargs)
        self.set_header('Authorization', b64encode(':'.join([self.customer_name, self.customer_api_key])))
        self.set_header('Content-Type', 'application/x-www-form-urlencoded')

    def get_method(self):
        return 'POST'


class OrderDetailsQuery(V1Query):
    def __init__(self, customer_api_key, customer_name, **kwargs):
        super(OrderDetailsQuery, self).__init__(customer_api_key, customer_name=customer_name, **kwargs)

    def get_path(self):
        return '/clients/retail/api/?action=order_view_details'

    def _subprocess_response(self, status, reason, response):
        certificate_details = None
        pending_reissue = None
        try:
            rspreturn = response['response']['return']
            certificate_details = CertificateDetails(**rspreturn['certificate_details'])
            pending_reissue = PendingReissue(**rspreturn['pending_reissue'])
        except KeyError:
            pass
        return OrderViewDetailsSucceededResponse(status, reason, certificate_details, pending_reissue)


class RetrieveCertificateQuery(V1Query):
    def __init__(self, customer_api_key, customer_name, **kwargs):
        super(RetrieveCertificateQuery, self).__init__(customer_api_key, customer_name=customer_name, **kwargs)

    def get_path(self):
        return '/clients/retail/api/?action=retrieve_certificate'

    def _subprocess_response(self, status, reason, response):
        order_id = None
        serial = None
        retrieved_certificate = None
        try:
            rspreturn = response['response']['return']
            order_id = rspreturn['order_id']
            serial = rspreturn['serial']
            retrieved_certificate = RetrievedCertificate(**rspreturn['certs'])
        except KeyError:
            pass
        return RetrieveCertificateSucceededResponse(status, reason, order_id, serial, retrieved_certificate)

if __name__ == '__main__':
    pass