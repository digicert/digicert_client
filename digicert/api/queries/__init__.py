#!/usr/bin/env python

from digicert.api import RetailApiRequest
from digicert.api.responses\
    import OrderViewDetailsSucceededResponse,\
    RetrieveCertificateSucceededResponse,\
    CertificateDetails,\
    PendingReissue,\
    RetrievedCertificate


class RetailApiQuery(RetailApiRequest):
    order_id = None

    def __init__(self, customer_name, customer_api_key, order_id, **kwargs):
        super(RetailApiQuery, self).__init__(customer_name, customer_api_key, **kwargs)
        self.order_id = order_id

        if not 'order_id' in self.__dict__:
            raise RuntimeError('No value provided for required property "order_id"')

    def _get_method(self):
        return 'POST'


class OrderDetailsQuery(RetailApiQuery):
    def __init__(self, customer_name, customer_api_key, order_id, **kwargs):
        super(OrderDetailsQuery, self).__init__(customer_name, customer_api_key, order_id, **kwargs)

    def _get_path(self):
        return '%s?action=order_view_details' % self._digicert_api_path

    def _subprocess_response(self, status, reason, response):
        try:
            rspreturn = response['response']['return']
            return OrderViewDetailsSucceededResponse(status, reason,
                                                     self._certificate_details_from_response(rspreturn),
                                                     self._pending_reissue_from_response(rspreturn))
        except KeyError:
            return OrderViewDetailsSucceededResponse(status, reason, None, None)

    def _certificate_details_from_response(self, response):
        if response:
            try:
                d = response['certificate_details']
                return CertificateDetails(order_id=_value_from_dict(d, 'order_id'),
                                          status=_value_from_dict(d, 'status'),
                                          product_name=_value_from_dict(d, 'product_name'),
                                          validity=_value_from_dict(d, 'validity'),
                                          org_unit=_value_from_dict(d, 'org_unit'),
                                          common_name=_value_from_dict(d, 'common_name'),
                                          sans=_value_from_dict(d, 'sans'),
                                          order_date=_value_from_dict(d, 'order_date'),
                                          valid_from=_value_from_dict(d, 'valid_from'),
                                          valid_till=_value_from_dict(d, 'valid_till'),
                                          server_type=_value_from_dict(d, 'server_type'),
                                          server_type_name=_value_from_dict(d, 'server_type_name'),
                                          site_seal_token=_value_from_dict(d, 'site_seal_token'))
            except KeyError:
                pass
        return None

    def _pending_reissue_from_response(self, response):
        if response:
            try:
                d = response['pending_reissue']
                return PendingReissue(common_name=_value_from_dict(d, 'common_name'),
                                      sans=_value_from_dict(d, 'sans'))
            except KeyError:
                pass
        return None


class RetrieveCertificateQuery(RetailApiQuery):
    def __init__(self, customer_name, customer_api_key, order_id, **kwargs):
        super(RetrieveCertificateQuery, self).__init__(customer_name, customer_api_key, order_id, **kwargs)

    def _get_path(self):
        return '%s?action=retrieve_certificate' % self._digicert_api_path

    def _subprocess_response(self, status, reason, response):
        try:
            rspreturn = response['response']['return']
            return RetrieveCertificateSucceededResponse(status, reason,
                                                        _value_from_dict(rspreturn, 'order_id'),
                                                        _value_from_dict(rspreturn, 'serial'),
                                                        self._certs_from_response(rspreturn))
        except KeyError:
            return RetrieveCertificateSucceededResponse(status, reason, None, None, None)

    def _certs_from_response(self, response):
        if response:
            try:
                d = response['certs']
                return RetrievedCertificate(certificate=_value_from_dict(d, 'certificate'),
                                            intermediate=_value_from_dict(d, 'intermediate'),
                                            root=_value_from_dict(d, 'root'),
                                            pkcs7=_value_from_dict(d, 'pkcs7'))
            except KeyError:
                pass
        return None


def _value_from_dict(d, key, default=None):
    if d and key and key in d:
        return d[key]
    return default


if __name__ == '__main__':
    pass