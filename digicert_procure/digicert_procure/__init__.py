#!/usr/bin/env python


class CertificateType(object):
    """Contains supported values for the 'certificate_type' property of OrderCertificateCommand."""

    SSLPLUS = 'sslplus'

    # Currently unsupported
    #UC = 'uc'
    #WILDCARD = 'wildcard'
    #EVSSL = 'evssl'
    #EVMULTI = 'evmulti'


class Validity(object):
    """Contains supported values for the 'validity' property of OrderCertificateCommand."""
    ONE_YEAR = 1
    TWO_YEARS = 2
    THREE_YEARS = 3


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


if __name__ == '__main__':
    pass
