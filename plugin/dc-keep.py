# copyright license from digicert??

__author__ = 'fish'

import six
from barbican.openstack.common import gettextutils as u
from barbican.common import utils
from barbican.plugin.interface import certificate_manager as cert

from digicert_procure import CertificateOrder
from digicert_procure import CertificateType
from digicert_procure import Validity
from httplib import HTTPSConnection

from oslo.config import cfg

DEBUG = True
CONF = cfg.CONF

digicert_plugin_opts = [
    cfg.StrOpt('account_id',
               help=u._('DigiCert account ID for authentication')),
    cfg.StrOpt('api_key',
               help=u._('DigiCert API Key for authentication')),
    cfg.StrOpt('dc_host',
               help=u._('DigiCert host for authentication'))

]

digicert_plugin_group = cfg.OptGroup(name='digicert_plugin',
                                     title='DigiCert Plugin Options')

CONF.register_group(digicert_plugin_group)
CONF.register_opts(digicert_plugin_opts, group=digicert_plugin_group)
LOG = utils.getLogger(__name__)

# constants for DC API request attributes
CERTIFICATE_TYPE = 'certificate_type'
CSR = 'csr'
VALIDITY = 'validity'
COMMON_NAME = 'common_name'
ORG_NAME = 'org_name'
ORG_ADDR1 = 'org_addr1'
ORG_ADDR2 = 'org_addr2'
ORG_CITY = 'org_city'
ORG_STATE = 'org_state'
ORG_ZIP = 'org_zip'
ORG_COUNTRY = 'org_country'
ORG_CONTACT_FIRST_NAME = 'org_contact_firstname'
ORG_CONTACT_LAST_NAME = 'org_contact_lastname'
ORG_CONTACT_EMAIL = 'org_contact_email'
ORG_CONTACT_TELEPHONE = 'org_contact_telephone'
SERVER_TYPE = 'server_type'
ORG_UNIT = 'org_unit'
SANS = 'sans'
TELEPHONE = 'telephone'
ORG_CONTACT_JOB_TITLE = 'org_contact_job_title'
ORG_CONTACT_TELEPHONE_EXTENSION = 'org_contact_telephone_ext'

validity_years = {
    '1': Validity.ONE_YEAR,
    '2': Validity.TWO_YEARS,
    '3': Validity.THREE_YEARS
}

# dict of DC request attributes, some are optional, #
# keys would represent what is sent through from the API
# values represent the mapping to our attribute name
DIGICERT_API_REQUEST_ATTRS = {
    CERTIFICATE_TYPE: CERTIFICATE_TYPE,
    CSR: CSR,
    VALIDITY: VALIDITY,
    COMMON_NAME: COMMON_NAME,
    ORG_NAME: ORG_NAME,
    ORG_ADDR1: ORG_ADDR1,
    ORG_CITY: ORG_CITY,
    ORG_STATE: ORG_STATE,
    ORG_ZIP: ORG_ZIP,
    ORG_COUNTRY: ORG_COUNTRY,
    ORG_CONTACT_FIRST_NAME: ORG_CONTACT_FIRST_NAME,
    ORG_CONTACT_LAST_NAME: ORG_CONTACT_LAST_NAME,
    ORG_CONTACT_EMAIL: ORG_CONTACT_EMAIL,
    ORG_CONTACT_TELEPHONE: ORG_CONTACT_TELEPHONE,
    SERVER_TYPE: SERVER_TYPE,
    ORG_UNIT: ORG_UNIT,
    SANS: SANS,
    ORG_ADDR2: ORG_ADDR2,
    TELEPHONE: TELEPHONE,
    ORG_CONTACT_JOB_TITLE: ORG_CONTACT_JOB_TITLE,
    ORG_CONTACT_TELEPHONE_EXTENSION: ORG_CONTACT_TELEPHONE_EXTENSION
    }

RESULT_STATUS = 'status'
RESULT_STATUS_MESSAGE = 'status_message'
RESULT_CERTIFICATE = 'certificate'
RESULT_INTERMEDIATES = 'intermediates'
RESULT_RETRY_MSEC = 'retry_msec'
RESULT_RETRY_METHOD = 'retry_method'
RESULT_STATUS_ATTRS = {RESULT_STATUS: '', RESULT_STATUS_MESSAGE: '', RESULT_CERTIFICATE: '', RESULT_INTERMEDIATES: '', RESULT_RETRY_MSEC: '', RESULT_RETRY_METHOD: ''}

class DigiCertCertificatePlugin(cert.CertificatePluginBase):
    """DigiCert certificate plugin to OpenStack Barbican secret store."""

    def __init__(self, conf=CONF):
        self.account_id = conf.digicert_plugin.account_id
        self.api_key = conf.digicert_plugin.api_key
        self.dc_host = conf.digicert_plugin.dc_host

        LOG.info('............. in digicert cert plugin init...........')
        LOG.info('AccountID: %s   API Key:   %s ' % (self.account_id, self.api_key))

        # TODO: remove this debug code
        if DEBUG:
            self.account_id = '84300'
            self.api_key = 'jv29zx9dnwq478229w3x499720t1ddlf'
            self.dc_host = 'ccdev.digicert.com'

        if self.api_key is None:
            raise ValueError(u._("Api Key is required"))

        if self.account_id is None and self.api_key == None:
            raise ValueError(u._("Account ID or API Key is required"))

        if self.dc_host is None:
            raise ValueError(u._("API Host is required"))


    def issue_certificate_request(self, order_id, order_meta, plugin_meta):
        """Create the initial order

        :param order_id: ID associated with the order
        :param order_meta: Dict of meta-data associated with the order
        :param plugin_meta: Plugin meta-data previously set by calls to
                            this plugin. Plugins may also update/add
                            information here which Barbican will persist
                            on their behalf
        :returns: A :class:`ResultDTO` instance containing the result
                  populated by the plugin implementation
        :rtype: :class:`ResultDTO`
        """
        response = _create_order(self, order_id, order_meta, plugin_meta)

        result = ''

        LOG.info('............. in digicert cert plugin issue cert request...........')
        if response.get(RESULT_RETRY_MSEC):
            result = cert.ResultDTO(cert.CertificateStatus.CLIENT_DATA_ISSUE_SEEN, status_message=response.get(RESULT_STATUS, '') + ' : ' + response.get(RESULT_STATUS_MESSAGE, ''))
            LOG.info('............. there was an error sending the request to the server.  Error: %s...........', result)
        else:
            result = cert.ResultDTO(cert.CertificateStatus.WAITING_FOR_CA, status_message=response.get(RESULT_STATUS_MESSAGE, ''))
            LOG.info('............. request for cert submitted successfully...........')
        return result

    def check_certificate_status(self, order_id, order_meta, plugin_meta):
        """Check status of the order

        :param order_id: ID associated with the order
        :param order_meta: Dict of meta-data associated with the order
        :param plugin_meta: Plugin meta-data previously set by calls to
                            this plugin. Plugins may also update/add
                            information here which Barbican will persist
                            on their behalf
        :returns: A :class:`ResultDTO` instance containing the result
                  populated by the plugin implementation
        :rtype: :class:`ResultDTO`
        """
        status = _get_order_status(self, order_id, order_meta, plugin_meta)
        result = ''
        if status.get(RESULT_RETRY_MSEC):
            result = cert.ResultDTO(cert.CertificateStatus.CLIENT_DATA_ISSUE_SEEN)
            LOG.info('............. there was an error sending the request to the server.  Error: %s...........', result)
        elif status.get(RESULT_CERTIFICATE):
            result = cert.ResultDTO(cert.CertificateStatus.CERTIFICATE_GENERATED)
            result.certificate = status.get(RESULT_CERTIFICATE)
            result.intermediates = status.get(RESULT_INTERMEDIATES)
        else:
            result = cert.ResultDTO(cert.CertificateStatus.WAITING_FOR_CA, status_message=status.get(RESULT_STATUS_MESSAGE, ''))
        print result.status
        return result

    def modify_certificate_request(self, order_id, order_meta, plugin_meta):
        """Update the order meta-data

        :param order_id: ID associated with the order
        :param order_meta: Dict of meta-data associated with the order
        :param plugin_meta: Plugin meta-data previously set by calls to
                            this plugin. Plugins may also update/add
                            information here which Barbican will persist
                            on their behalf
        :returns: A :class:`ResultDTO` instance containing the result
                  populated by the plugin implementation
        :rtype: :class:`ResultDTO`
        """
        raise NotImplementedError  # pragma: no cover

    def cancel_certificate_request(self, order_id, order_meta, plugin_meta):
        """Cancel the order

        :param order_id: ID associated with the order
        :param order_meta: Dict of meta-data associated with the order.
        :param plugin_meta: Plugin meta-data previously set by calls to
                            this plugin. Plugins may also update/add
                            information here which Barbican will persist
                            on their behalf
        :returns: A :class:`ResultDTO` instance containing the result
                  populated by the plugin implementation
        :rtype: :class:`ResultDTO`
        """
        raise NotImplementedError  # pragma: no cover

    def supports(self, certificate_spec):
        """Returns if the plugin supports the certificate type.

        :param certificate_spec: Contains details on the certificate to
                                 generate the certificate order
        :returns: boolean indicating if the plugin supports the certificate
                  type
        """
        # raise NotImplementedError  # pragma: no cover
        # TODO: what types of certs are requested.  What does DigiCert support?
        return True

def _create_order(self, order_id, order_meta, plugin_meta):
    # TODO: some input validation or certificate type mapping or attribute key mapping
    order = CertificateOrder(self.dc_host, self.api_key, customer_name=self.account_id, conn=HTTPSConnection(self.dc_host))
    response = order.place(**order_meta)

    print response
    if len(response.get('id')):
        RESULT_STATUS_ATTRS[RESULT_STATUS_MESSAGE] = response.get('id')
    else:
        LOG.info(response.get('response'))
        RESULT_STATUS_ATTRS[RESULT_RETRY_MSEC] = 300000
        RESULT_STATUS_ATTRS[RESULT_STATUS_MESSAGE] = response.get('response', response.get('description'))
        RESULT_STATUS_ATTRS[RESULT_STATUS] = response.get('result', response.get('code'))

    return dict(RESULT_STATUS_ATTRS)

def _get_order_status(self, order_id, order_meta, plugin_meta):

    # TODO: remove hard coded connection class
    order = CertificateOrder(self.dc_host, self.api_key, customer_name=self.account_id, conn=HTTPSConnection(self.dc_host))
    response = order.view(order_id=order_id)

    print response
    if response.get(RESULT_STATUS) == 'issued':
        order_meta['order_id'] = order_id
        certificate = order.download(**order_meta)
        print certificate
        RESULT_STATUS_ATTRS[RESULT_CERTIFICATE] = certificate.get('certificates').get('certificate')
        RESULT_STATUS_ATTRS[RESULT_INTERMEDIATES] = certificate.get('certificates').get('intermediate')
    elif response.get(RESULT_STATUS) == 'pending issuance':
        RESULT_STATUS_ATTRS[RESULT_STATUS_MESSAGE] = response.get(RESULT_STATUS)
    return dict(RESULT_STATUS_ATTRS)


# take attributes input from the API request and map them to our own API attribute names
def _map_attributes(input_attrs):
    for old, new in DIGICERT_API_REQUEST_ATTRS.iteritems():
        value = input_attrs.get(old, None)
        if value is None:
            continue

        input_attrs[new] = value
        del input_attrs[old]
    return input_attrs


if __name__ == '__main__':
    _order_meta = {
            'certificate_type': 'sslplus',
            'csr': '''-----BEGIN CERTIFICATE REQUEST-----
MIICnjCCAYYCAQAwWTELMAkGA1UEBhMCVVMxDTALBgNVBAgMBFV0YWgxDjAMBgNV
BAcMBXByb3ZvMRUwEwYDVQQKDAxkaWdpY2VydCBpbmMxFDASBgNVBAMMC3lvdS5t
YXguY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Y+FJGm4VrgV
c1JUbVWiooM20TrqS+dmkabh80BPWFEfXUHbXeLAjXOgLworMnEFSLJiCSuZQndl
eHCUHW/3+hyDsSwhEmpdjUXHEqVhVEmSBLc478PMKGQNi2snpf3VSBdpNbnrADsZ
OfQxbkPnh7yy5yQYiLGv4ibFPT3rVKd2XzbHwz49mhAT8yF261/Kge7ES/N97955
4ftaLusSiN7Z1WKsmp/k1niA8b6AD2jmlfJ9FSwFd7yfcIexrNiXHNlp/qHq8vWs
7jeknb2lrrLPejrwfLc4ZG6nwF6QUju69nC3ywjKfDM2UpDfqOYKL9jVM4kh2yKc
NzS17DhaHQIDAQABoAAwDQYJKoZIhvcNAQEFBQADggEBAFJxj8AiDAL1Vda/N5eG
NP3ZZ382Y8YwXcAlcvID8eQlUz7IjJLRgMRYURZBc9dsN04gyLDvGZapAvyQpQ0s
8UHwTJpYhqEIuCOHJCcq4aVMHZFs/92r6I+tpo6VkpkyLR22tOPV+XJMKvYRoE1M
ZpP4suFpPRo+oCAQOl0i2/t+sHRzqig/JqRLC3DxypNmh3YnF3Q4W9jIoaNhmeMa
eq815GMZj5hUFKHZdXdRGib2xi4i2Kv8gyExqrFw8B7WbYrlokC8ab+nWr+4Vund
LsetAq44TVoFZwty69i7RcXhpjzDpGqaF0CWIgj1YpjKvqXZtcTS8YabfcQVkaLX
czQ=
-----END CERTIFICATE REQUEST-----''',
            'validity': '1',
            'common_name': 'fake.com',
            'org_name': 'Fake Co.',
            'org_addr1': '123 Nowhere Lane',
            'org_city': 'Nowhere',
            'org_state': 'UT',
            'org_zip': '12345',
            'org_country': 'US',
            'org_contact_firstname': 'Bill',
            'org_contact_lastname': 'Billson',
            'org_contact_email': 'bbillson@fakeco.biz',
            'org_contact_telephone': '2345556789'}

    _plugin_meta = {
        'server_type': '2',
        'org_unit': 'FakeCo',
        'sans': 'Fake Company, Fake Inc.',
        'org_addr2': 'Infinitieth Floor',
        'telephone': '2345556789',
        'org_contact_job_title': 'CTO',
        'org_contact_telephone_ext': '5150'}

    dc = DigiCertCertificatePlugin()
    result = dc.issue_certificate_request('00570280', _order_meta, _plugin_meta)
    print 'issue_certificate: '
    print result.status
    # order_status = dc.check_certificate_status('581907', _order_meta, _plugin_meta)
    # print 'order status: '
    # print order_status
    # print order_status.certificate
