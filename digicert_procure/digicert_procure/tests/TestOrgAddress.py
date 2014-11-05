#!/usr/bin/env python

import unittest

from .. import OrgAddress


class TestOrgAddress(unittest.TestCase):
    def test_construct(self):
        addr = OrgAddress('123 Nowhere Lane', 'Nowhere', 'ut', '12345', 'us')
        self.assertEqual('123 Nowhere Lane', addr.addr1)
        self.assertEqual('Nowhere', addr.city)
        self.assertEqual('UT', addr.state)
        self.assertEqual('12345', addr.zip)
        self.assertEqual('US', addr.country)

    def test_construct_with_optionals(self):
        addr = OrgAddress(addr1='123 Nowhere Lane',
                          addr2='Sweet Suite',
                          telephone='8765554321',
                          city='Nowhere',
                          state='ut',
                          zip='12345',
                          country='us')
        self.assertEqual('123 Nowhere Lane', addr.addr1)
        self.assertEqual('123 Nowhere Lane', addr.addr)
        self.assertEqual('Sweet Suite', addr.addr2)
        self.assertEqual('8765554321', addr.telephone)
        self.assertEqual('Nowhere', addr.city)
        self.assertEqual('UT', addr.state)
        self.assertEqual('12345', addr.zip)
        self.assertEqual('US', addr.country)

if __name__ == '__main__':
    unittest.main()