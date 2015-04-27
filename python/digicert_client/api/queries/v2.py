from ..queries import Query


class V2Query(Query):
    _base_path = '/services/v2'

    def __init__(self, customer_api_key, **kwargs):
        super(V2Query, self).__init__(customer_api_key=customer_api_key, customer_name=None)
        self.set_header('X-DC-DEVKEY', customer_api_key)
        self.set_header('Content-Type', 'application/json')

    def get_method(self):
        return 'GET'

    def _is_failure_response(self, response):
        return 'errors' in response


class ViewOrderDetailsQuery(V2Query):
    order_id = None

    def __init__(self, customer_api_key, **kwargs):
        """
        Construct a ViewOrderDetailsQuery, a CQRS-style query object representing a request
        to view the details of an already-placed certificate order.  This the V2 version of
        the query.


        :param customer_api_key: the customer's DigiCert API key
        :param kwargs:
        :return:
        """
        super(ViewOrderDetailsQuery, self).__init__(customer_api_key=customer_api_key, **kwargs)
        if 'order_id' in kwargs:
            self.order_id = kwargs['order_id']
        if self.order_id is None:
            raise KeyError('No value provided for required property "order_id"')

    def get_path(self):
        return '%s/order/certificate/%s' % (self._base_path, self.order_id)

    def _subprocess_response(self, status, reason, response):
        return self._make_response(status, reason, response)


class ViewOrdersQuery(V2Query):

    def __init__(self, customer_api_key):
        super(ViewOrdersQuery, self).__init__(customer_api_key=customer_api_key)

    def get_path(self):
        return '%s/order/certificate' % self._base_path

    def _subprocess_response(self, status, reason, response):
        return self._make_response(status, reason, response)


class DownloadCertificateQuery(V2Query):
    order_id = None
    certificate_id = None

    def __init__(self, customer_api_key, **kwargs):
        """
        Construct a DownloadCertificateQuery, a CQRS-style query object representing a request
        to download the certificate resulting from a certificate order.  This is the V2 version
        of the query.

        :param customer_api_key: the customer's DigiCert API key
        :param kwargs:
        :return:
        """
        super(DownloadCertificateQuery, self).__init__(customer_api_key=customer_api_key, **kwargs)
        if 'order_id' in kwargs:
            self.order_id = kwargs['order_id']
        if 'certificate_id' in kwargs:
            self.certificate_id = kwargs['certificate_id']
        if self.certificate_id is None and self.order_id is None:
            raise KeyError('No value provided for required properties "certificate_id", "order_id" (at least one is required)')

    def get_path(self):
        # if we don't have a certificate ID, then we know it's a retail account, and we call the download by order ID endpoint
        if self.certificate_id:
            url = '%s/certificate/%s/download/format/pem_all' % (self._base_path, self.certificate_id)
        else:
            url = '%s/certificate/download/order/%s' % (self._base_path, self.order_id)
        return url

    def _subprocess_response(self, status, reason, response):
        certs = []
        if '-----' in response:
            for cert in response.split('-----'):
                cert = cert.strip()
                if len(cert) and not cert.startswith('BEGIN ') and not cert.startswith('END '):
                    certs.append(cert)
            if 3 != len(certs):
                raise RuntimeError('Unexpected number of certificates in certificate chain')
            return self._make_response(status, reason, {
                'certificates': {
                    'certificate': '-----BEGIN CERTIFICATE-----\r\n' + certs[0] + '\r\n-----END CERTIFICATE-----',
                    'intermediate': '-----BEGIN CERTIFICATE-----\r\n' + certs[1] + '\r\n-----END CERTIFICATE-----',
                    'root': '-----BEGIN CERTIFICATE-----\r\n' + certs[2] + '\r\n-----END CERTIFICATE-----'
                }
            })
        else:
            # this must be a zip file containing certs
            return response # this is a zip file


class MyUserQuery(V2Query):
    def __init__(self, customer_api_key):
        """
        Construct a MyUserQuery, a CQRS-style query object to get details about the
        user represented by the provided customer api key.

        :param customer_api_key: the customer's DigiCert API key
        :return:
        """
        super(MyUserQuery, self).__init__(customer_api_key=customer_api_key)

    def get_path(self):
        return '%s/user/me' % self._base_path

    def _subprocess_response(self, status, reason, response):
        return response


class OrganizationByContainerIdQuery(V2Query):
    def __init__(self, customer_api_key, container_id):
        """
        Construct an OrganizationByContainerIdQuery, a CQRS-style query object to obtain
        a list of organizations associated with the supplied container id.

        :param customer_api_key: the customer's DigiCert API key
        :param container_id: the container id for the organizations
        :return:
        """
        super(OrganizationByContainerIdQuery, self).__init__(customer_api_key=customer_api_key)
        self.container_id = container_id

    def get_path(self):
        return '%s/organization?container_id=%s' % (self._base_path, self.container_id)

    def _subprocess_response(self, status, reason, response):
        orgs = []
        for entry in response['organizations']:
            orgs.append(entry)
        return orgs


class DomainByContainerIdQuery(V2Query):
    def __init__(self, customer_api_key, container_id):
        """
        Construct a DomainByContainerIdQuery, a CQRS-style query object to obtain
        a list of domains associated with the supplied container id.

        :param customer_api_key: the customer's DigiCert API key
        :param container_id:  the container id for the domains
        :return:
        """
        super(DomainByContainerIdQuery, self).__init__(customer_api_key=customer_api_key)
        self.container_id = container_id

    def get_path(self):
        return '%s/domain?container_id=%s' % (self._base_path, self.container_id)

    def _subprocess_response(self, status, reason, response):
        domains = []
        for entry in response['domains']:
            domains.append(entry)
        return domains

if __name__ == '__main__':
    pass