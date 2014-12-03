# Copyright (c) 2013-2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from barbican.openstack.common import gettextutils as u
from barbican.plugin.interface import certificate_manager as cert
from digicert_procure import CertificateOrder
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

# TODO(Jeff Fischer) move these or are they necessary
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
    """DigiCert certificate plugin to OpenStack Barbican secret store."""

    def __init__(self, conf=CONF):
        self.account_id = conf.digicert_plugin.account_id
        self.api_key = conf.digicert_plugin.api_key
        self.dc_host = conf.digicert_plugin.dc_host

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

        result = ''
        if response.get(RESULT_RETRY_MSEC):
            status_message = '%s : %s' % (response.get(RESULT_STATUS),
                                          response.get(RESULT_STATUS_MESSAGE))
            cert_status = cert.CertificateStatus.CA_UNAVAILABLE_FOR_REQUEST
            result = cert.ResultDTO(cert_status, status_message=status_message)
        else:
            status_message = response.get(RESULT_STATUS_MESSAGE)
            result = cert.ResultDTO(cert.CertificateStatus.WAITING_FOR_CA,
                                    status_message=status_message)
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


# TODO(Jeff Fischer) abstract these, or maybe they aren't necessary
def _create_order(self, order_id, order_meta, plugin_meta):
    # TODO(Jeff Fischer) future input validation or
    # TODO(Jeff Fischer) certificate type mapping or attribute key mapping
    # TODO(Jeff Fischer) returned id should be persisted through plugin_meta
    order = CertificateOrder(self.dc_host, self.api_key,
                             customer_name=self.account_id)
    response = order.place(**order_meta)

    if response.get('id'):
        RESULT_ATTRIBUTES[RESULT_STATUS_MESSAGE] = response.get('id')
        # plugin_meta['id'] = response.get('id')
    else:
        RESULT_ATTRIBUTES[RESULT_RETRY_MSEC] = 300000
        RESULT_ATTRIBUTES[RESULT_STATUS_MESSAGE] = (response.get('response')
                                                    or
                                                    response.get('description'))
        RESULT_ATTRIBUTES[RESULT_STATUS] = (response.get('result')
                                            or
                                            response.get('code'))

    return dict(RESULT_ATTRIBUTES)


def _get_order_status(self, order_id, order_meta, plugin_meta):
    # TODO(Jeff Fischer) order_id coming through belongs to Barbican.
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
