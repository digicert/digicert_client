from base64 import b64encode

from ..queries import Query


class V1Query(Query):
    order_id = None

    def __init__(self, customer_api_key, customer_name, **kwargs):
        super(V1Query, self).__init__(customer_api_key, customer_name=customer_name, **kwargs)
        self.set_header('Authorization', b64encode(':'.join([self.customer_name, self.customer_api_key])))
        self.set_header('Content-Type', 'application/x-www-form-urlencoded')
        if self.order_id is None:
            raise KeyError('No value provided for required property "order_id"')

    def get_method(self):
        return 'POST'


class ViewOrderDetailsQuery(V1Query):
    def __init__(self, customer_api_key, customer_name, **kwargs):
        """
        Construct a ViewOrderDetailsQuery, a CQRS-style query object representing a request
        to view the details of an already-placed certificate order.  This the V1 version of
        the query.


        :param customer_api_key: the customer's DigiCert API key
        :param customer_name: the customer's DigiCert account number, e.g. '012345'
        :param kwargs:
        :return:
        """
        super(ViewOrderDetailsQuery, self).__init__(customer_api_key, customer_name=customer_name, **kwargs)

    def get_path(self):
        return '/clients/retail/api/?action=order_view_details'

    def _subprocess_response(self, status, reason, response):
        cert_details = response['response']['return']['certificate_details']
        response = {
            'id': cert_details['order_id'],
            'status': cert_details['status'],
            'certificate': {
                'common_name': cert_details['common_name'],
            },
            'product': {
                'name': cert_details['product_name']
            },
        }
        if 'validity' in cert_details:
            response['certificate']['validity'] = cert_details['validity']
        if 'sans' in cert_details:
            response['certificate']['dns_names'] = cert_details['sans']
        if 'valid_from' in cert_details:
            response['certificate']['date_created'] = cert_details['valid_from']
        if 'org_unit' in cert_details:
            response['certificate']['organization_units'] = [cert_details['org_unit']]
        if 'server_type' in cert_details or 'server_type_name' in cert_details:
            response['certificate']['server_platform'] = {}
            if 'server_type' in cert_details:
                response['certificate']['server_platform']['id'] = cert_details['server_type']
            if 'server_type_name' in cert_details:
                response['certificate']['server_platform']['name'] = cert_details['server_type_name']
        return self._make_response(status, reason, response)


class DownloadCertificateQuery(V1Query):
    def __init__(self, customer_api_key, customer_name, **kwargs):
        """
        Construct a DownloadCertificateQuery, a CQRS-style query object representing a request
        to download the certificate resulting from a certificate order.  This is the V1 version
        of the query.

        :param customer_api_key: the customer's DigiCert API key
        :param customer_name: the customer's DigiCert account number, e.g. '012345'
        :param kwargs:
        :return:
        """
        super(DownloadCertificateQuery, self).__init__(customer_api_key, customer_name=customer_name, **kwargs)

    def get_path(self):
        return '/clients/retail/api/?action=retrieve_certificate'

    def _subprocess_response(self, status, reason, response):
        certs = response['response']['return']['certs']
        rsp = {
            'certificates': {
                'certificate': certs['certificate'].strip(),
                'intermediate': certs['intermediate'].strip(),
            }
        }
        if 'root' in certs:
            rsp['certificates']['root'] = certs['root'].strip()
        if 'pkcs7' in certs:
            rsp['certificates']['pkcs7'] = certs['pkcs7'].strip()
        return self._make_response(status, reason, rsp)

if __name__ == '__main__':
    pass