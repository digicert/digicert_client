#!/usr/bin/env python

from .https import VerifiedHTTPSConnection
from .api import Request
from .api.commands.v1 import OrderCertificateCommand as OrderCertificateCommandV1
from .api.commands.v2 import OrderCertificateCommand as OrderCertificateCommandV2
from .api.commands.v2 import UploadCSRCommand as UploadCSRCommandV2
from .api.queries.v1 import ViewOrderDetailsQuery as ViewOrderDetailsQueryV1
from .api.queries.v2 import ViewOrderDetailsQuery as ViewOrderDetailsQueryV2
from .api.queries.v2 import ViewOrdersQuery as ViewOrdersQueryV2
from .api.queries.v1 import DownloadCertificateQuery as DownloadCertificateQueryV1
from .api.queries.v2 import DownloadCertificateQuery as DownloadCertificateQueryV2
from .api.queries.v2 import MyUserQuery, OrganizationByContainerIdQuery, DomainByContainerIdQuery


class CertificateType(object):
    """Contains supported values for the 'certificate_type' property of OrderCertificateCommand."""

    SSLPLUS = 'sslplus'
    UC = 'uc'
    WILDCARD = 'wildcard'
    EVSSL = 'evssl'
    EVMULTI = 'evmulti'

    def __iter__(self):
        for certtype in [self.SSLPLUS, self.UC, self.WILDCARD, self.EVSSL, self.EVMULTI, ]:
            yield certtype


class Validity(object):
    """Contains supported values for the 'validity' property of OrderCertificateCommand."""
    ONE_YEAR = 1
    TWO_YEARS = 2
    THREE_YEARS = 3

    def __iter__(self):
        for period in [self.ONE_YEAR, self.TWO_YEARS, self.THREE_YEARS, ]:
            yield period


class CertificateOrder(object):
    """High-level representation of a certificate order, for placing new orders or working with existing orders."""

    def __init__(self, host, customer_api_key, customer_name=None, conn=None):
        """
        Constructor for CertificateOrder.

        :param host: Host of the web service APIs
        :param customer_api_key: Customer's API key for use in authorizing requests
        :param customer_name: Optional customer account ID.  If left blank, the V2 API will be used;
        if not, the V1 API will be used.
        :param conn: Optional connection class instance, defaults to VerifiedHTTPSConnection to the provided host
        :return:
        """
        self.host = host
        self.customer_api_key = customer_api_key
        self.customer_name = customer_name if customer_name and len(customer_name.strip()) else None
        self.conn = conn if conn else VerifiedHTTPSConnection(self.host)

    def _get_container_id_for_active_user(self):
        cmd = MyUserQuery(customer_api_key=self.customer_api_key)
        me = Request(cmd, self.host, self.conn).send()
        return me['container']['id']

    def _get_matching_organization_id(self, container_id, **kwargs):
        cmd = OrganizationByContainerIdQuery(customer_api_key=self.customer_api_key, container_id=container_id)
        orgs = Request(cmd, self.host, self.conn).send()
        matching_org = None
        for org in orgs:
            if org['name'] != kwargs['org_name'] or \
                org['address'] != kwargs['org_addr1'] or \
                org['city'] != kwargs['org_city'] or \
                org['state'].lower() != kwargs['org_state'].lower() or \
                org['zip'] != kwargs['org_zip'] or \
                org['country'].lower() != kwargs['org_country'].lower():
                continue
            elif 'org_addr2' in kwargs and (not 'address2' in org or org['address2'] != kwargs['org_addr2']):
                continue
            elif 'org_unit' in kwargs and (not 'unit' in org or org['unit'] != kwargs['org_unit']):
                continue
            elif 'organization_contact' in org:
                org_contact = org['organization_contact']
                if org_contact['first_name'] != kwargs['org_contact_firstname'] or \
                    org_contact['last_name'] != kwargs['org_contact_lastname'] or \
                    org_contact['email'] != kwargs['org_contact_email'] or \
                    org_contact['telephone'] != kwargs['org_contact_telephone']:
                    continue
                elif 'org_contact_job_title' in kwargs and \
                        (not 'job_title' in org['organization_contact'] or
                             org['organization_contact']['job_title'] != kwargs['org_contact_job_title']):
                    continue
                elif 'org_contact_telephone_ext' in kwargs and \
                        (not 'telephone_ext' in org['organization_contact'] or
                             org['organization_contact']['telephone_ext'] != kwargs['org_contact_telephone_ext']):
                    continue
            matching_org = org
        return matching_org['id'] if matching_org else None

    def _has_matching_domain(self, container_id, organization_id, common_name):
        cmd = DomainByContainerIdQuery(customer_api_key=self.customer_api_key, container_id=container_id)
        domains = Request(cmd, self.host, self.conn).send()
        for domain in domains:
            if domain['organization']['id'] == organization_id and domain['name'] == common_name:
                return True
        return False

    def place(self, **kwargs):
        """Place this order."""
        if self.customer_name:
            cmd = OrderCertificateCommandV1(customer_api_key=self.customer_api_key,
                                            customer_name=self.customer_name,
                                            **kwargs)
            response = Request(action=cmd, host=self.host, conn=self.conn).send()
            return response
        else:
            # This is a multi-request interaction
            container_id = self._get_container_id_for_active_user()
            org_id = self._get_matching_organization_id(container_id, **kwargs)
            if org_id is None:
                return {'status': 404, 'reason': 'Not Found', 'response': 'No matching organization found'}
            if not self._has_matching_domain(container_id=container_id,
                                             organization_id=org_id,
                                             common_name=kwargs['common_name']):
                return {'status': 404, 'reason': 'Not Found', 'response': 'No matching domain found'}
            cmd = OrderCertificateCommandV2(customer_api_key=self.customer_api_key, organization_id=org_id, **kwargs)
            response = Request(action=cmd, host=self.host, conn=self.conn).send()
            return response

    def view(self, digicert_order_id=None, **kwargs):
        """Get details about an existing order."""
        if digicert_order_id:
            kwargs['order_id'] = digicert_order_id
        if self.customer_name:
            cmd = ViewOrderDetailsQueryV1(customer_api_key=self.customer_api_key,
                                          customer_name=self.customer_name,
                                          **kwargs)
        else:
            cmd = ViewOrderDetailsQueryV2(customer_api_key=self.customer_api_key, **kwargs)
        return Request(action=cmd, host=self.host, conn=self.conn).send()

    def view_all(self):
        cmd = ViewOrdersQueryV2(customer_api_key=self.customer_api_key)
        return Request(action=cmd, host=self.host, conn=self.conn).send()

    def upload_csr(self, digicert_order_id=None, csr_text=None, **kwargs):
        if digicert_order_id:
            kwargs['order_id'] = digicert_order_id
        if csr_text:
            kwargs['csr'] = csr_text
        cmd = UploadCSRCommandV2(customer_api_key=self.customer_api_key, **kwargs)
        return Request(action=cmd, host=self.host, conn=self.conn).send()

    def download(self, digicert_order_id=None, digicert_certificate_id=None, **kwargs):
        """Retrieve an issued certificate represented by this order."""
        if digicert_order_id:
            if 'order_id' not in kwargs:
                kwargs['order_id'] = digicert_order_id
        if digicert_certificate_id:
            kwargs['certificate_id'] = digicert_certificate_id
        if self.customer_name:
            cmd = DownloadCertificateQueryV1(customer_api_key=self.customer_api_key,
                                             customer_name=self.customer_name,
                                             **kwargs)
        else:
            if not 'certificate_id' in kwargs and 'order_id' in kwargs:
                cmd = ViewOrderDetailsQueryV2(customer_api_key=self.customer_api_key, **kwargs)
                order_details_rsp = Request(action=cmd, host=self.host, conn=self.conn).send()
                if 'certificate' in order_details_rsp and 'id' in order_details_rsp['certificate']:
                    kwargs['certificate_id'] = order_details_rsp['certificate']['id']
            cmd = DownloadCertificateQueryV2(customer_api_key=self.customer_api_key, **kwargs)
        return Request(action=cmd, host=self.host, conn=self.conn).send()


if __name__ == '__main__':
    pass
