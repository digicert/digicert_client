#!/usr/bin/env python

import unittest

from .. import Org, OrgAddress, OrgContact

name = 'Fake Co.'
addr1 = '123 Nowhere Lane'
city = 'Nowhere'
state = 'UT'
zip = '12345'
country = 'US'
addr = OrgAddress(addr1, city, state, zip, country)
firstname = 'Bill'
lastname = 'Billson'
email = 'bbillson@fakeco.biz'
telephone = '2345556798'
contact = OrgContact(firstname, lastname, email, telephone)


class TestOrg(unittest.TestCase):
    def verify_fields(self, org):
        self.assertEqual(addr1, org.addr.addr1)
        self.assertEqual(city, org.addr.city)
        self.assertEqual(state, org.addr.state)
        self.assertEqual(zip, org.addr.zip)
        self.assertEqual(country, org.addr.country)
        self.assertEqual(firstname, org.contact.firstname)
        self.assertEqual(lastname, org.contact.lastname)
        self.assertEqual(email, org.contact.email)
        self.assertEqual(telephone, org.contact.telephone)

    def test_construct(self):
        org = Org(name, addr, contact)
        self.assertEqual(name, org.name)
        self.assertEqual(addr, org.addr)
        self.assertEqual(contact, org.contact)
        self.verify_fields(org)

    def test_construct_with_optionals_in_addr(self):
        oaddr = OrgAddress(addr1=addr1,
                           addr2='Sweet Suite',
                           city=city,
                           state=state,
                           zip=zip,
                           country=country,
                           telephone='8765554321')
        org = Org(name, oaddr, contact)
        self.assertEqual(name, org.name)
        self.assertEqual(oaddr, org.addr)
        self.assertEqual(contact, org.contact)
        self.verify_fields(org)
        self.assertEqual('Sweet Suite', org.addr.addr2)
        self.assertEqual('8765554321', org.addr.telephone)

    def test_construct_with_optionals_in_contact(self):
        ocontact = OrgContact(firstname=firstname,
                              lastname=lastname,
                              email=email,
                              telephone=telephone,
                              telephone_ext='9009',
                              job_title='Senior Peasant')
        org = Org(name, addr, ocontact)
        self.assertEqual(name, org.name)
        self.assertEqual(addr, org.addr)
        self.assertEqual(ocontact, org.contact)
        self.verify_fields(org)
        self.assertEqual('9009', org.contact.telephone_ext)
        self.assertEqual('Senior Peasant', org.contact.job_title)

    def test_construct_with_invalid_addr(self):
        try:
            Org(name, addr1, contact)
            self.fail()
        except TypeError:
            pass

    def test_construct_with_invalid_contact(self):
        try:
            Org(name, addr, firstname)
            self.fail()
        except TypeError:
            pass

if __name__ == '__main__':
    unittest.main()