__author__ = 'fish'

from barbican.common import utils
from barbican.openstack.common import gettextutils as u

from barbican.plugin.interface import certificate_manager as cert
from digicert_procure import CertificateOrder
from digicert_procure import Validity
from oslo.config import cfg

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

# dict of DC request attributes, some are optional,
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
RESULT_ATTRIBUTES = {
    RESULT_STATUS: '',
    RESULT_STATUS_MESSAGE: '',
    RESULT_CERTIFICATE: '',
    RESULT_INTERMEDIATES: '',
    RESULT_RETRY_MSEC: '',
    RESULT_RETRY_METHOD: ''
}


class DigiCertCertificatePlugin(cert.CertificatePluginBase):
    """DigiCert certificate plugin to OpenStack Barbican secret store"""

    def __init__(self, conf=CONF):
        self.account_id = conf.digicert_plugin.account_id
        self.api_key = conf.digicert_plugin.api_key
        self.dc_host = conf.digicert_plugin.dc_host

        LOG.info('..in digicert cert plugin init..')
        LOG.info('AccountID: %s APIKey: %s ' % (self.account_id, self.api_key))

        if self.api_key is None:
            raise ValueError(u._("Api Key is required"))

        if self.account_id is None and self.api_key is None:
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

        LOG.info('..in digicert cert plugin issue cert request..')

        result = ''
        if response.get(RESULT_RETRY_MSEC):
            status_message = '%s : %s' % (response.get(RESULT_STATUS),
                                          response.get(RESULT_STATUS_MESSAGE))
            cert_status = cert.CertificateStatus.CLIENT_DATA_ISSUE_SEEN
            result = cert.ResultDTO(cert_status, status_message=status_message)
            LOG.info('Error sending the request to the server: %s', result)
        else:
            status_message = response.get(RESULT_STATUS_MESSAGE)
            result = cert.ResultDTO(cert.CertificateStatus.WAITING_FOR_CA,
                                    status_message=status_message)
            LOG.info('..request for cert submitted successfully..')
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
            cert_status = cert.CertificateStatus.CLIENT_DATA_ISSUE_SEEN
            result = cert.ResultDTO(cert_status)
            LOG.info('Error sending the request to the server: %s', result)
        elif status.get(RESULT_CERTIFICATE):
            cert_status = cert.CertificateStatus.CERTIFICATE_GENERATED
            result = cert.ResultDTO(cert_status)
            result.certificate = status.get(RESULT_CERTIFICATE)
            result.intermediates = status.get(RESULT_INTERMEDIATES)
        else:
            status_message = status.get(RESULT_STATUS_MESSAGE)
            result = cert.ResultDTO(cert.CertificateStatus.WAITING_FOR_CA,
                                    status_message=status_message)
        return result

    def modify_certificate_request(self, order_id, order_meta, plugin_meta):
        """Update the order meta-data  This operation is not supported

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
        """Cancel the order  This operation is not supported

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
        return True


def _create_order(self, order_id, order_meta, plugin_meta):
    # TODO: future input validation or
    # TODO: certificate type mapping or attribute key mapping
    order = CertificateOrder(self.dc_host, self.api_key,
                             customer_name=self.account_id)
    response = order.place(**order_meta)

    if len(response.get('id')):
        RESULT_ATTRIBUTES[RESULT_STATUS_MESSAGE] = response.get('id')
    else:
        LOG.info(response.get('response'))
        RESULT_ATTRIBUTES[RESULT_RETRY_MSEC] = 300000
        RESULT_ATTRIBUTES[RESULT_STATUS_MESSAGE] = response.get('response') \
            or \
            response.get('description')
        RESULT_ATTRIBUTES[RESULT_STATUS] = response.get('result') \
            or \
            response.get('code')

    return dict(RESULT_ATTRIBUTES)


def _get_order_status(self, order_id, order_meta, plugin_meta):
    order = CertificateOrder(self.dc_host, self.api_key,
                             customer_name=self.account_id)
    response = order.view(order_id=order_id)

    if response.get(RESULT_STATUS) == 'issued':
        order_meta['order_id'] = order_id
        certificate = order.download(**order_meta)
        result_cert = certificate.get('certificates').get('certificate')
        RESULT_ATTRIBUTES[RESULT_CERTIFICATE] = result_cert
        result_inter = certificate.get('certificates').get('intermediate')
        RESULT_ATTRIBUTES[RESULT_INTERMEDIATES] = result_inter
    elif response.get('status') == 'pending issuance':
        RESULT_ATTRIBUTES[RESULT_STATUS_MESSAGE] = response.get('status')
    return dict(RESULT_ATTRIBUTES)


def _map_attributes(input_attributes):
    """
    rudimentary mapping from input attributes to digicert attribute names
    :param input_attrs:
    :return:
    """
    for old, new in DIGICERT_API_REQUEST_ATTRS.iteritems():
        value = input_attributes.get(old, None)
        if value is None:
            continue

        input_attributes[new] = value
        del input_attributes[old]
    return input_attributes


if __name__ == '__main__':
    pass
