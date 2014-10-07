# copyright license from digicert??

__author__ = 'fishy, mryan'

import six
from barbican.openstack.common import gettextutils as u
from barbican.plugin.interface import certificate_manager as cert

from oslo.config import cfg

from digicert.api.commands import OrderCertificateCommand
from digicert.api.commands import RetailCommand

# set any options we need, such as URL

# inherit the certificatepluginbase class

# implement the methods in the parent

# check for authentication, any validation of input parameters

# call our digicert client

CONF = cfg.CONF

symantec_plugin_opts = [
    cfg.StrOpt('username',
               help=u._('DigiCert username for authentication')),
    cfg.StrOpt('password',
               help=u._('DigiCert password for authentication')),
    cfg.StrOpt('url',
               help=u._('Domain of DigiCert API'))
]

dc_plugin_group = cfg.OptGroup(name='digicert_plugin',
                                     title='DigiCert Plugin Options')

CONF.register_group(dc_plugin_group)
CONF.register_opts(symantec_plugin_opts, group=dc_plugin_group)

class DigiCertBarbicanCertificatePlugin(cert.CertificatePluginBase):
    """Symantec certificate plugin."""

    def __init__(self, conf=CONF):
        pass
        # TODO: validate auth for digicert client
        #
        # self.username = conf.symantec_plugin.username
        # if self.username == None:
        #     raise ValueError(u._("username is required"))
        #
        # self.password = conf.symantec_plugin.password
        # if self.password == None:
        #     raise ValueError(u._("password is required"))
        #
        # self.url = conf.symantec_plugin.url
        # if self.url == None:
        #     raise ValueError(u._("url is required"))

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
        raise NotImplementedError  # pragma: no cover

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
        raise NotImplementedError  # pragma: no cover

    def supports(self, certificate_spec):
        """Returns if the plugin supports the certificate type.

        :param certificate_spec: Contains details on the certificate to
                                 generate the certificate order
        :returns: boolean indicating if the plugin supports the certificate
                  type
        """
        # raise NotImplementedError  # pragma: no cover
        # TODO: what types of certs are requested.  Can DC support each cert?
        return True

# this method needs to submit an order via the DC Client
def _create_order(self, order_meta, plugin_meta):
    retail = RetailCommand('customer_name', 'customer_api_key', **order_meta)
    # TODO: eventually, there will need to be a mapper of some sort here but for now just passing through the data because it's defined in the API

    # call digicert client passing through the data and submit retail order
    return cert.ResultDTO()

def _modify_order(self, order_meta, plugin_meta):
    pass

def _get_order_status(self, plugin_meta):
    pass

def _cancel_order(self, plugin_meta):
    pass









# sample dict mapping keys a manual way.  Is there a simpler way?
# name_mapping = {
#     'key': 'first_name',
# }
#
# dic = your_dict
#
# # Can't iterate over collection being modified,
# # so change the iterable being iterated.
# for old, new in name_mapping.iteritems():
#     value = dic.get(old, None)
#     if value is None:
#         continue
#
#     dic[new] = value
#     del dic[old]




# TODO: is this a class that can use as messaging between DC CA and client?
# @six.add_metaclass(abc.ABCMeta)
class CertificateEventPluginBase(object):
    """Base class for certificate eventing plugins.

    This class is the base plugin contract for issuing certificate related
    events from Barbican.
    """

    def notify_certificate_is_ready(
            self, project_id, order_ref, container_ref):
        """Notify that a certificate has been generated and is ready to use.

        :param project_id: Project/tenant ID associated with this certificate
        :param order_ref: HATEOS reference URI to the submitted Barbican Order
        :param container_ref: HATEOS reference URI to the Container storing
               the certificate
        :returns: None
        """
        raise NotImplementedError  # pragma: no cover

    def notify_ca_is_unavailable(
            self, project_id, order_ref, error_msg, retry_in_msec):
        """Notify that the certificate authority (CA) isn't available.

        :param project_id: Project/tenant ID associated with this order
        :param order_ref: HATEOS reference URI to the submitted Barbican Order
        :param error_msg: Error message if it is available
        :param retry_in_msec: Delay before attempting to talk to the CA again.
               If this is 0, then no attempt will be made.
        :returns: None
        """
        raise NotImplementedError  # pragma: no cover
