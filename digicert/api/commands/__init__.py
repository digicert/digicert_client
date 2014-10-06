#!/usr/bin/env python

from digicert.api import RetailApiRequest


class RetailApiCommand(RetailApiRequest):
    def __init__(self, customer_name, customer_api_key, **kwargs):
        RetailApiRequest.__init__(self, customer_name, customer_api_key, **kwargs)

    def _get_method(self):
        return 'POST'


class OrderCertificateCommand(RetailApiCommand):
    certificate_type = None
    csr = None
    validity = None
    server_type = -1
    org_unit = None
    common_name = None
    sans = None
    org_name = None
    org_addr1 = None
    org_addr2 = None
    org_city = None
    org_state = None
    org_zip = None
    org_country = None
    telephone = None
    org_contact_job_title = None
    org_contact_firstname = None
    org_contact_lastname = None
    org_contact_email = None
    org_contact_telephone = None
    org_contact_telephone_ext = None

    def __init__(self,
                 customer_name,
                 customer_api_key,
                 certificate_type,
                 csr,
                 validity,
                 common_name,
                 org_name,
                 org_addr1,
                 org_city,
                 org_state,
                 org_zip,
                 org_country,
                 org_contact_firstname,
                 org_contact_lastname,
                 org_contact_email,
                 org_contact_telephone,
                 **kwargs):
        RetailApiCommand.__init__(self, customer_name, customer_api_key, **kwargs)
        self.certificate_type = certificate_type
        self.csr = csr
        self.validity = int(validity)
        self.common_name = common_name
        self.org_name = org_name
        self.org_addr1 = org_addr1
        self.org_city = org_city
        self.org_state = org_state
        self.org_zip = org_zip
        self.org_country = org_country
        self.org_contact_firstname = org_contact_firstname
        self.org_contact_lastname = org_contact_lastname
        self.org_contact_email = org_contact_email
        self.org_contact_telephone = org_contact_telephone

    def _process_special(self, key, value):
        if 'server_type' == key:
            self.server_type = int(value)
            return True
        return False




if __name__ == '__main__':
    pass