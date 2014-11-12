#!/usr/bin/env python

import types


class CertificateDetails(object):
    """Represents the 'certificate_details' portion of an order details query response."""

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

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if 'sans' == key:
                if isinstance(value, types.StringTypes):
                    if len(value):
                        value = [value]
                    else:
                        value = []
            setattr(self, key, value)

    def __str__(self):
        return '\n'.join(['%s: %s' % (k, v) for k, v in self.__dict__.items()])


class PendingReissue(object):
    """Represents the 'pending_reissue' portion of an order details query response."""

    common_name = None
    sans = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if 'sans' == key:
                if isinstance(value, types.StringTypes):
                    if len(value):
                        value = [value]
                    else:
                        value = []
            setattr(self, key, value)

    def __str__(self):
        return '\n'.join(['%s: %s' % (k, v) for k, v in self.__dict__.items()])


class RetrievedCertificate(object):
    """
    Represents the 'certs' portion of the RetrieveCertificateQuery response.

    When constructed, this object will contain the end-entity certificate that
    was ordered, a list of any intermediates, and the root certificate, along with
    the pkcs7 for the certificates.  The intermediates will always be represented
    as a list even if there is only one.
    """
    certificate = None
    intermediate = None
    root = None
    pkcs7 = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if 'intermediate' == key:
                if isinstance(value, types.StringTypes):
                    if len(value):
                        value = [value]
                    else:
                        value = []
            setattr(self, key, value)
        if self.intermediate is None:
            self.intermediate = []

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
    """Base class to represent the 'return' section of the DigiCert Retail API calls."""
    status = None
    reason = None

    def __init__(self, status, reason):
        """
        RetailApiReturn constructor

        :param status: The HTTP status code returned from the request, e.g. 200
        :param reason: The HTTP reason code returned from the request, e.g. 'OK'
        :return:
        """
        self.status = status
        self.reason = reason

    def __str__(self):
        return 'Status: %s\nReason: %s' % (self.status, self.reason)


class OrderCertificateReturn(RetailApiReturn):
    """Represents the 'return' section for a certificate order request."""

    order_id = None

    def __init__(self, status, reason, order_id):
        """
        OrderCertificateReturn constructor

        :param status: The HTTP status code returned from the request, e.g. 200
        :param reason: The HTTP reason code returned from the request, e.g. 'OK'
        :param order_id: Unique order identifier for this certificate order
        :return:
        """
        super(OrderCertificateReturn, self).__init__(status, reason)
        self.order_id = order_id

    def __str__(self):
        return '\n'.join([RetailApiReturn.__str__(self), 'Order ID: %s' % self.order_id])


class OrderStatusReturn(RetailApiReturn):
    """Represents the 'return' section for a certificate order status request."""

    certificate_details = None
    pending_reissue = None

    def __init__(self, status, reason, certificate_details, pending_reissue):
        """
        OrderStatusReturn constructor

        :param status: The HTTP status code returned from the request, e.g. 200
        :param reason: The HTTP reason code returned from the request, e.g. 'OK'
        :param certificate_details: A CertificateDetails object describing the ordered certificate, status, etc.
        :param pending_reissue: A PendingReissue object, if there is a pending reissue, or None
        :return:
        """
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
    """Represents the 'return' section for a certificate retrieval request."""

    order_id = None
    serial = None
    certs = None

    def __init__(self, status, reason, order_id, serial, certificates):
        """
        RetrieveCertificateReturn constructor

        :param status: The HTTP status code returned from the request, e.g. 200
        :param reason: The HTTP reason code returned from the request, e.g. 'OK'
        :param order_id: Unique order identifier for this certificate order
        :param serial: The serial number of the certificate
        :param certificates: A Certificates object describing the issued certificate, intermediate(s), and root
        :return:
        """
        super(RetrieveCertificateReturn, self).__init__(status, reason)
        self.order_id = order_id
        self.serial = serial
        self.certs = certificates

    def __str__(self):
        return '\n'.join([RetailApiReturn.__str__(self)] + ['%s: %s' % (k, v) for k, v in self.__dict__.items()])


class RetailApiResponse(object):
    """Base class representing DigiCert Retail API request responses."""

    result = None

    def __init__(self, result):
        """
        RetailApiResponse base class constructor

        :param result: The result of the request, e.g. 'success' or 'failure'
        :return:
        """
        self.result = result


class RequestFailedResponse(RetailApiResponse):
    """Represents a failure response to a DigiCert Retail API request"""

    error_codes = []

    def __init__(self, error_codes):
        """
        RequestFailedResponse constructor

        :param error_codes: List of error_code mappings.  A single error code is usually of
        the form { 'code' : 'description' }.  A RequestFailedResponse may have multiple error
        codes, all contained within the error_codes list provided at construction time.
        Usually, just obtaining the JSON value for the 'error_codes' field in the response
        payload and providing that value to the constructor is sufficient.
        :return:
        """
        super(RequestFailedResponse, self).__init__('failure')
        self.error_codes = error_codes

    def __str__(self):
        s = []
        for ec in self.error_codes:
            s += ['\t%s - %s' % (k, v) for k, v in ec.items()]
        return '\n'.join(['Request Failed:'] + s)


class RequestSucceededResponse(RetailApiResponse):
    """
    Represents a success response to a DigiCert Retail API request.
    Usually the success response will be represented by a more
    detailed subclass.
    """

    return_obj = None

    def __init__(self, return_obj):
        """
        RequestSucceededResponse constructor.

        :param return_obj: The object represented by the 'return' field in the response data.
        :return:
        """
        super(RequestSucceededResponse, self).__init__('success')
        self.return_obj = return_obj

    def __str__(self):
        return self.return_obj.__str__()


class OrderCertificateSucceededResponse(RequestSucceededResponse):
    """Represents the response to a successful certificate order request."""

    def __init__(self, status, reason, order_id):
        """
        Creates a success response object for an OrderCertificateCommand.

        :param status: The HTTP status code returned from the request, e.g. 200
        :param reason: The HTTP reason code returned from the request, e.g. 'OK'
        :param order_id: Unique identifier for the certificate order
        :return:
        """
        super(OrderCertificateSucceededResponse,
              self).__init__(OrderCertificateReturn(status,
                                                    reason,
                                                    order_id))


class OrderViewDetailsSucceededResponse(RequestSucceededResponse):
    """Represents the response to a successful request to view order details."""

    def __init__(self, status, reason, certificate_details, pending_reissue):
        """
        Creates a success response object for an OrderViewDetailsQuery.

        :param status: The HTTP status code returned from the request, e.g. 200
        :param reason: The HTTP reason code returned from the request, e.g. 'OK'
        :param certificate_details: A CertificateDetails object created from the response data
        :param pending_reissue: A PendingReissue object created from the response data, or None
        :return:
        """
        super(OrderViewDetailsSucceededResponse,
              self).__init__(OrderStatusReturn(status,
                                               reason,
                                               certificate_details,
                                               pending_reissue))


class RetrieveCertificateSucceededResponse(RequestSucceededResponse):
    """Represents the response to a successful request to retrieve an issued certificate."""

    def __init__(self, status, reason, order_id, serial, certificates):
        """
        Creates a success response object for a RetrieveCertificateQuery.

        :param status: The HTTP status code returned from the request, e.g. 200
        :param reason: The HTTP reason code returned from the request, e.g. 'OK'
        :param order_id: Unique identifier for the certificate order
        :param serial: Serial number for the certificate
        :param certificates: A Certificates object representing the created certificate, intermediate(s), and root
        :return:
        """
        super(RetrieveCertificateSucceededResponse,
              self).__init__(RetrieveCertificateReturn(status,
                                                       reason,
                                                       order_id,
                                                       serial,
                                                       certificates))


if __name__ == '__main__':
    pass