# Copyright (c) 2013-2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
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

RESULT_STATUS = 'status'
RESULT_STATUS_MESSAGE = 'status_message'


class DigiCertCertificatePlugin(cert.CertificatePluginBase):
    """DigiCert certificate plugin to OpenStack Barbican secret store."""

    def __init__(self, conf=CONF):
        self.account_id = conf.digicert_plugin.account_id
        self.api_key = conf.digicert_plugin.api_key
        self.dc_host = conf.digicert_plugin.dc_host

        if self.api_key is None:
            raise ValueError(u._("Api Key is required"))

        if self.dc_host is None:
            raise ValueError(u._("API Host is required"))

        self.orderclient = CertificateOrder(self.dc_host, self.api_key,
                                            customer_name=self.account_id)

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

        # TODO(Jeff Fischer) future input validation or
        # TODO(Jeff Fischer) product type mapping or attribute key mapping
        # TODO(Jeff Fischer) returned id to be persisted through plugin_meta
        response = self.orderclient.place(**order_meta)

        if not response.get('id'): ##### is this correct logic??????? OJO
            status_msg = '{0}:{1}'.format(response.get(RESULT_STATUS),
                                          response.get(RESULT_STATUS_MESSAGE))

            cert_status = cert.CertificateStatus.CA_UNAVAILABLE_FOR_REQUEST

            result = cert.ResultDTO(cert_status, status_message=status_msg)
        else:
            plugin_meta['id'] = response.get('id')
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

        digicert_order_id = plugin_meta.get('id')
        response = self.orderclient.view(digicert_order_id, **order_meta)

        if response.get(RESULT_STATUS) == 'issued':
            certificate = self.orderclient.download(digicert_order_id,
                                                    **order_meta)
            result_cert = certificate.get('certificates').get('certificate')
            result_inter = certificate.get('certificates').get('intermediate')
            cert_status = cert.CertificateStatus.CERTIFICATE_GENERATED
            result = cert.ResultDTO(cert_status)
            result.certificate = result_cert
            result.intermediates = result_inter
        elif response.get(RESULT_STATUS) == 'pending issuance':
            status_message = response.get(RESULT_STATUS_MESSAGE)
            result = cert.ResultDTO(cert.CertificateStatus.WAITING_FOR_CA,
                                    status_message=status_message)
        else:
            cert_status = cert.CertificateStatus.CLIENT_DATA_ISSUE_SEEN
            result = cert.ResultDTO(cert_status)

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
