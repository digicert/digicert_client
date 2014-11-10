#!/usr/bin/env python

import unittest

from .. import OrgContact


class TestOrgContact(unittest.TestCase):
    def test_construct(self):
        contact = OrgContact('Bill', 'Billson', 'bbillson@fakeco.biz', '2345556789')
        self.assertEqual('Bill', contact.firstname)
        self.assertEqual('Billson', contact.lastname)
        self.assertEqual('bbillson@fakeco.biz', contact.email)
        self.assertEqual('2345556789', contact.telephone)

    def test_construct_with_optionals(self):
        contact = OrgContact(firstname='Bill',
                             lastname='Billson',
                             job_title='Senior Peasant',
                             telephone='2345556789',
                             telephone_ext='9009',
                             email='bbillson@fakeco.biz')
        self.assertEqual('Bill', contact.firstname)
        self.assertEqual('Billson', contact.lastname)
        self.assertEqual('bbillson@fakeco.biz', contact.email)
        self.assertEqual('2345556789', contact.telephone)
        self.assertEqual('Senior Peasant', contact.job_title)
        self.assertEqual('9009', contact.telephone_ext)

if __name__ == '__main__':
    unittest.main()
