#!/usr/bin/env python

from .https import VerifiedHTTPSConnection
from .api import Request
from .api.commands.v1 import OrderCertificateCommand as OrderCertificateCommandV1
from .api.commands.v2 import OrderCertificateCommand as OrderCertificateCommandV2
from .api.queries.v1 import OrderDetailsQuery as OrderDetailsQueryV1
from .api.queries.v2 import OrderDetailsQuery as OrderDetailsQueryV2
from .api.queries.v1 import RetrieveCertificateQuery as RetrieveCertificateQueryV1
from .api.queries.v2 import RetrieveCertificateQuery as RetrieveCertificateQueryV2
from .api.queries.v2 import MyUserQuery


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


class OrgAddress(object):
    """Address portion of an organization that owns a certificate."""
    def __init__(self, addr1=None, city=None, state=None, zip=None, country=None, **kwargs):
        """
        Constructor for OrgAddress.

        Optional arguments e.g. addr2, telephone can be supplied via kwargs.

        :param addr1: line 1 of the organization's address
        :param city: the city of organization's address
        :param state: the state/province of the organization's address
        :param zip: the zip or postal code of the organization's address
        :param country: the two-character abbreviation of the organization's country
        :param kwargs:
        :return:
        """
        self.addr = self.addr1 = addr1
        self.city = city
        self.state = state.upper()
        self.zip = zip
        self.country = country.upper()
        for k, v in kwargs.items():
            setattr(self, k, v)


class OrgContact(object):
    """Contact portion of an organization that owns a certificate."""
    def __init__(self, firstname, lastname, email, telephone, **kwargs):
        """
        Constructor for OrgContact.

        Optional arguments e.g. job_title, telephone_ext can be supplied via kwargs.

        :param firstname: the first name of the organization contact
        :param lastname: the last name of the organization contact
        :param email: the email address of the organization contact
        :param telephone: the telephone number of the organization contact
        :param kwargs:
        :return:
        """
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.telephone = telephone
        for k, v in kwargs.items():
            setattr(self, k, v)


class Org(object):
    """Organization that owns a certificate."""
    def __init__(self, name, addr, contact, **kwargs):
        """
        Constructor for Org.  It is comprised of a name, an OrgAddress, and an OrgContact.

        :param name: Organization name.
        :param addr: OrgAddress portion of the organization.
        :param contact: OrgContact portion of the organization.
        :param kwargs:
        :return:
        """
        self.name = name
        if not isinstance(addr, OrgAddress):
            raise TypeError('"addr" parameter is of type "%s.%s", expected "%s.%s"' %
                            (addr.__class__.__module__,
                             addr.__class__.__name__,
                             OrgAddress.__module__,
                             OrgAddress.__name__))
        else:
            self.addr = addr
        if not isinstance(contact, OrgContact):
            raise TypeError('"contact" parameter is of type "%s.%s", expected "%s.%s' %
                            (contact.__class__.__module__,
                             contact.__class__.__module__,
                             OrgAddress.__module__,
                             OrgContact.__name__))
        else:
            self.contact = contact
        for k, v in kwargs.items():
            setattr(self, k, v)


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

    def place(self, **kwargs):
        """Place this order."""
        if self.customer_name:
            cmd = OrderCertificateCommandV1(customer_api_key=self.customer_api_key,
                                            customer_name=self.customer_name,
                                            **kwargs)
            return Request(action=cmd, host=self.host, conn=self.conn).send()
        else:
            # This is a multi-request interaction
            cmd = MyUserQuery(customer_api_key=self.customer_api_key)
            me = Request(cmd, self.host, self.conn).send()
            container_id = me.container.id
            response = container_id
            #cmd = OrderCertificateCommandV2(customer_api_key=self.customer_api_key, **kwargs)
            #return Request(action=cmd, host=self.host, conn=self.conn).send()
            return response

    def get_details(self, **kwargs):
        """Get details about an existing order."""
        if self.customer_name:
            cmd = OrderDetailsQueryV1(customer_api_key=self.customer_api_key,
                                      customer_name=self.customer_name,
                                      **kwargs)
        else:
            cmd = OrderDetailsQueryV2(customer_api_key=self.customer_api_key, **kwargs)
        return Request(action=cmd, host=self.host, conn=self.conn).send()

    def retrieve(self, **kwargs):
        """Retrieve an issued certificate represented by this order."""
        if self.customer_name:
            cmd = RetrieveCertificateQueryV1(customer_api_key=self.customer_api_key,
                                             customer_name=self.customer_name,
                                             **kwargs)
        else:
            cmd = RetrieveCertificateQueryV2(customer_api_key=self.customer_api_key, **kwargs)
        return Request(action=cmd, host=self.host, conn=self.conn).send()


if __name__ == '__main__':
    pass
