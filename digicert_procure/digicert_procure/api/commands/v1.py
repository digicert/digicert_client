from base64 import b64encode

from . import Command


class V1Command(Command):
    def __init__(self, customer_api_key, customer_name=None, **kwargs):
        super(V1Command, self).__init__(customer_api_key=customer_api_key, customer_name=customer_name, **kwargs)
        self.set_header('Authorization', b64encode(':'.join([self.customer_name, self.customer_api_key])))
        self.set_header('Content-Type', 'application/x-www-form-urlencoded')


class OrderCertificateCommand(V1Command):
    def __init__(self,
                 customer_api_key,
                 customer_name=None,
                 **kwargs):
        """
        Constructs an OrderCertificateCommand, a CQRS-style Command object for ordering certificates.

        All required parameters must be specified in the constructor positionally or by keyword.
        Optional parameters may be specified via kwargs.

        :param customer_api_key: the customer's DigiCert API key
        :param certificate_type: type of certificate being ordered (see OrderCertificateCommand.CertificateType)
        :param csr: Base64-encoded text of the certificate signing request for this certificate
        :param validity: years of validity for this certificate (see OrderCertificateCommand.Validity)
        :param common_name: the name to be secured in the certificate, e.g. example.com
        :param org: the organization which owns the certificate
        :param customer_name: the customer's DigiCert account number, e.g. '012345'  This parameter
        is optional.  If provided, the DigiCert Retail API will be used; if not, the DigiCert CertCentral API
        will be used.
        :param kwargs:
        :return:
        """
        super(OrderCertificateCommand, self).__init__(customer_api_key, customer_name, **kwargs)

        for field in ['certificate_type', 'csr', 'validity', 'common_name',
                      'org_name', 'org_addr1', 'org_city', 'org_state', 'org_zip', 'org_country',
                      'org_contact_firstname', 'org_contact_lastname', 'org_contact_email', 'org_contact_telephone']:
            if not field in self.__dict__:
                raise KeyError('No value provided for required property "%s"' % field)

    def get_path(self):
        return '/clients/retail/api/?action=order_certificate'

    def _process_special(self, key, value):
        if 'server_type' == key:
            self.server_type = int(value)
            return True
        elif 'validity' == key:
            self.validity = int(value)
            return True
        return False

    def _subprocess_response(self, status, reason, response):
        if response['response']['result'] == 'failure':
            return self._make_response(status, reason, response['response']['error_codes'])
        order_id = response['response']['return']['order_id']
        return self._make_response(status, reason, {'id': order_id})


if __name__ == '__main__':
    pass