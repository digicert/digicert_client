#!/usr/bin/env python

import types


class CertificateDetails(object):
    order_id = None
    status = None
    product_name = None
    validity = None
    org_unit = None
    common_name = None
    sans = None
    order_date = None
    valid_from = None
    valid_till = None
    server_type = 0
    server_type_name = None
    site_seal_token = None

    def __init__(self,
                 order_id,
                 status,
                 product_name,
                 validity,
                 org_unit,
                 common_name,
                 sans,
                 order_date,
                 valid_from,
                 valid_till,
                 server_type,
                 server_type_name,
                 site_seal_token,
                 **kwargs):
        self.order_id = order_id
        self.status = status
        self.product_name = product_name
        self.validity = validity
        self.org_unit = org_unit
        self.common_name = common_name
        if isinstance(sans, types.StringTypes):
            if len(sans):
                self.sans = [sans]
            else:
                self.sans = []
        else:
            self.sans = sans
        self.order_date = order_date
        self.valid_from = valid_from
        self.valid_till = valid_till
        self.server_type = int(server_type)
        self.server_type_name = server_type_name
        self.site_seal_token = site_seal_token
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return '\n'.join(['%s: %s' % (k, v) for k, v in self.__dict__.items()])


class PendingReissue(object):
    common_name = None
    sans = None

    def __init__(self, common_name, sans):
        self.common_name = common_name
        if sans is None:
            self.sans = []
        elif isinstance(sans, types.StringTypes):
            if len(sans):
                self.sans = [sans]
            else:
                self.sans = []
        else:
            self.sans = sans

    def __str__(self):
        return '\n'.join(['%s: %s' % (k, v) for k, v in self.__dict__.items()])


class RetrievedCertificate(object):
    certificate = None
    intermediate = None
    root = None
    pkcs7 = None

    def __init__(self, certificate, intermediate, root, pkcs7):
        if intermediate is None:
            self.intermediate = []
        elif isinstance(intermediate, types.StringTypes):
            if len(intermediate):
                self.intermediate = [intermediate]
            else:
                self.intermediate = []
        self.certificate = certificate
        self.root = root
        self.pkcs7 = pkcs7

    def __str__(self):
        s = []
        if self.certificate:
            s += ['certificate:%s' % self.certificate]
        for intermediate in self.intermediate:
            s += ['intermediate:%s' % intermediate]
        if self.root:
            s += ['root:%s' % self.root]
        if self.pkcs7:
            s += ['pkcs7:%s' % self.pkcs7]
        return '\n'.join(s).strip()


class RetailApiReturn(object):
    status = None
    reason = None

    def __init__(self, status, reason):
        self.status = status
        self.reason = reason

    def __str__(self):
        return 'Status: %s\nReason: %s' % (self.status, self.reason)


class OrderCertificateReturn(RetailApiReturn):
    order_id = None

    def __init__(self, status, reason, order_id):
        super(OrderCertificateReturn, self).__init__(status, reason)
        self.order_id = order_id

    def __str__(self):
        return '\n'.join([RetailApiReturn.__str__(self), 'Order ID: %s' % self.order_id])


class OrderStatusReturn(RetailApiReturn):
    certificate_details = None
    pending_reissue = None

    def __init__(self, status, reason, certificate_details, pending_reissue):
        super(OrderStatusReturn, self).__init__(status, reason)
        self.certificate_details = certificate_details
        self.pending_reissue = pending_reissue

    def __str__(self):
        s = [RetailApiReturn.__str__(self)]
        if self.certificate_details:
            s += ['Certificate Details:', str(self.certificate_details)]
        if self.pending_reissue:
            s += ['Pending Reissue:', str(self.pending_reissue)]
        return '\n'.join(s)


class RetrieveCertificateReturn(RetailApiReturn):
    order_id = None
    serial = None
    certs = None

    def __init__(self, status, reason, order_id, serial, certificates):
        super(RetrieveCertificateReturn, self).__init__(status, reason)
        self.order_id = order_id
        self.serial = serial
        self.certs = certificates

    def __str__(self):
        return '\n'.join([RetailApiReturn.__str__(self)] + ['%s: %s' % (k, v) for k, v in self.__dict__.items()])


class RetailApiResponse(object):
    result = None

    def __init__(self, result):
        self.result = result


class RequestFailedResponse(RetailApiResponse):
    error_codes = []

    def __init__(self, error_codes):
        super(RequestFailedResponse, self).__init__('failure')
        self.error_codes = error_codes

    def __str__(self):
        s = []
        for ec in self.error_codes:
            s += ['\t%s - %s' % (k, v) for k, v in ec.items()]
        return '\n'.join(['Request Failed:'] + s)


class RequestSucceededResponse(RetailApiResponse):
    return_obj = None

    def __init__(self, return_obj):
        super(RequestSucceededResponse, self).__init__('success')
        self.return_obj = return_obj

    def __str__(self):
        return self.return_obj.__str__()


class OrderCertificateSucceededResponse(RequestSucceededResponse):
    def __init__(self, status, reason, order_id):
        super(OrderCertificateSucceededResponse,
              self).__init__(OrderCertificateReturn(status,
                                                    reason,
                                                    order_id))


class OrderViewDetailsSucceededResponse(RequestSucceededResponse):
    def __init__(self, status, reason, certificate_details, pending_reissue):
        super(OrderViewDetailsSucceededResponse,
              self).__init__(OrderStatusReturn(status,
                                               reason,
                                               certificate_details,
                                               pending_reissue))


class RetrieveCertificateSucceededResponse(RequestSucceededResponse):
    def __init__(self, status, reason, order_id, serial, certificates):
        super(RetrieveCertificateSucceededResponse,
              self).__init__(RetrieveCertificateReturn(status,
                                                       reason,
                                                       order_id,
                                                       serial,
                                                       certificates))


if __name__ == '__main__':
    pass