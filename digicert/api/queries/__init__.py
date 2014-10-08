#!/usr/bin/env python

from digicert.api import RetailApiRequest
from digicert.api.responses\
    import OrderViewDetailsSucceededResponse,\
    RetrieveCertificateSucceededResponse,\
    CertificateDetails,\
    PendingReissue,\
    RetrievedCertificate


class RetailApiQuery(RetailApiRequest):
    def __init__(self, customer_name, customer_api_key, **kwargs):
        RetailApiRequest.__init__(self, customer_name, customer_api_key, **kwargs)

    def _get_method(self):
        return 'POST'


class OrderDetailsQuery(RetailApiQuery):
    order_id = None

    def __init__(self, customer_name, customer_api_key, order_id, **kwargs):
        RetailApiQuery.__init__(self, customer_name, customer_api_key, **kwargs)
        self.order_id = order_id

    def _get_path(self):
        return '%s?action=order_view_details' % self._digicert_api_path

    def _subprocess_response(self, status, reason, response):
        certificate_details = None
        pending_reissue = None
        if 'response' in response:
            if 'return' in response['response']:
                rspreturn = response['response']['return']
                certificate_details = self._certificate_details_from_response(rspreturn)
                pending_reissue = self._pending_reissue_from_response(rspreturn)
        return OrderViewDetailsSucceededResponse(status, reason, certificate_details, pending_reissue)

    def _certificate_details_from_response(self, response):
        if not 'certificate_details' in response:
            return None
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

    def _pending_reissue_from_response(self, response):
        if not 'pending_reissue' in response:
            return None
        d = response['pending_reissue']
        return PendingReissue(common_name=_value_from_dict(d, 'common_name'),
                              sans=_value_from_dict(d, 'sans'))


class RetrieveCertificateQuery(RetailApiQuery):
    order_id = None

    def __init__(self, customer_name, customer_api_key, order_id, **kwargs):
        RetailApiQuery.__init__(self, customer_name, customer_api_key, **kwargs);
        self.order_id = order_id

    def _get_path(self):
        return '%s?action=retrieve_certificate' % self._digicert_api_path

    def _subprocess_response(self, status, reason, response):
        order_id = None
        serial = None
        certificates = None
        if 'response' in response:
            if 'return' in response['response']:
                rspreturn = response['response']['return']
                order_id = _value_from_dict(rspreturn, 'order_id')
                serial = _value_from_dict(rspreturn, 'serial')
                certificates = self._certs_from_response(rspreturn)
        return RetrieveCertificateSucceededResponse(status, reason, order_id, serial, certificates)

    def _certs_from_response(self, response):
        if not 'certs' in response:
            return None
        d = response['certs']
        return RetrievedCertificate(certificate=_value_from_dict(d, 'certificate'),
                                    intermediate=_value_from_dict(d, 'intermediate'),
                                    root=_value_from_dict(d, 'root'),
                                    pkcs7=_value_from_dict(d, 'pkcs7'))


def _value_from_dict(d, key, default=None):
    if key in d:
        return d[key]
    return default


if __name__ == '__main__':
    pass