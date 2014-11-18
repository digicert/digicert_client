#!/usr/bin/env python

import unittest
from urlparse import parse_qs

from .. import CertificateType, Validity
from ..api.commands.v1 import OrderCertificateCommand


class TestOrderCertificateCommand(unittest.TestCase):
    _customer_name = '12345'
    _customer_api_key = 'abapsdrtaewrh89249sbs89as0d'
    _api_host = 'localhost'
    _api_path = '/clients/retail/api/?action=order_certificate'
    _requireds_dict = {
        'certificate_type': 'sslplus',
        'csr': 'fakecsr',
        'validity': '1',
        'common_name': 'fakeco.biz',
        'org_name': 'Fake Co',
        'org_addr1': '123 Nowhere Lane',
        'org_city': 'Nowhere',
        'org_state': 'UT',
        'org_zip': '12345',
        'org_country': 'US',
        'org_contact_firstname': 'William',
        'org_contact_lastname': 'Billson',
        'org_contact_email': 'bbillson@fakeco.biz',
        'org_contact_telephone': '2345556789',
    }
    _optionals_dict = dict(_requireds_dict.items() + {
        'org_addr2': 'Infinitieth Floor',
        'telephone': '2345556789',
        'org_contact_job_title': 'Janitor',
        'org_contact_telephone_ext': '1001',
        'server_type': '2',
        'org_unit': 'FakeCo',
        'sans': ['www.fakeco.biz', 'fake.co.uk']}.items())

    def validate(self, o):
        self.assertEqual(o.customer_name, '12345')
        self.assertEqual(o.customer_api_key, 'abapsdrtaewrh89249sbs89as0d')
        self.assertEqual(o.certificate_type, 'sslplus')
        self.assertEqual(o.csr, 'fakecsr')
        self.assertEqual(o.validity, 1)
        self.assertEqual(o.common_name, 'fakeco.biz')
        self.assertEqual(o.org_name, 'Fake Co')
        self.assertEqual(o.org_addr1, '123 Nowhere Lane')
        self.assertEqual(o.org_city, 'Nowhere')
        self.assertEqual(o.org_state, 'UT')
        self.assertEqual(o.org_zip, '12345')
        self.assertEqual(o.org_country, 'US')
        self.assertEqual(o.org_contact_firstname, 'William')
        self.assertEqual(o.org_contact_lastname, 'Billson')
        self.assertEqual(o.org_contact_email, 'bbillson@fakeco.biz')
        self.assertEquals(o.org_contact_telephone, '2345556789')

    def validate_opt(self, o):
        self.assertEqual(o.server_type, 2)
        self.assertEqual(o.org_unit, 'FakeCo')
        self.assertEqual(o.sans, ['www.fakeco.biz', 'fake.co.uk'])
        self.assertEqual(o.org_addr2, 'Infinitieth Floor')
        self.assertEqual(o.telephone, '2345556789')
        self.assertEqual(o.org_contact_job_title, 'Janitor')
        self.assertEqual(o.org_contact_telephone_ext, '1001')

    def get_occ(self, additional_args):
        return OrderCertificateCommand(customer_name=self._customer_name,
                                       customer_api_key=self._customer_api_key,
                                       **additional_args)

    def test_construct(self):
        self.validate(self.get_occ(self._requireds_dict))

    def test_construct_optionals(self):
        occ = self.get_occ(self._optionals_dict)
        self.validate(occ)
        self.validate_opt(occ)

    def test_get_auth(self):
        occ = self.get_occ(self._requireds_dict)
        self.assertEqual('MTIzNDU6YWJhcHNkcnRhZXdyaDg5MjQ5c2JzODlhczBk', occ.get_headers()['Authorization'])

    def test_get_payload(self):
        actuals = {'customer_api_key': self._customer_api_key, 'customer_name': self._customer_name,
             'certificate_type': 'sslplus', 'csr': 'fakecsr', 'validity': '1', 'common_name': 'fakeco.biz',
             'org_name': 'Fake Co', 'org_addr1': '123 Nowhere Lane', 'org_city': 'Nowhere',
             'org_state': 'UT', 'org_zip': '12345', 'org_country': 'US',
             'org_contact_firstname': 'William', 'org_contact_lastname': 'Billson',
             'org_contact_email': 'bbillson@fakeco.biz', 'org_contact_telephone': '2345556789'}
        occ = self.get_occ(self._requireds_dict)
        payload = occ.get_params()
        self.assertTrue(len(payload) > 0)
        d = parse_qs(payload)
        for k in d.keys():
            self.assertEqual([actuals[k]], d[k])
        self.assertEqual(len(actuals), len(d))

    def test_get_payload_optionals(self):
        actuals = {'customer_api_key': self._customer_api_key, 'customer_name': self._customer_name,
             'certificate_type': 'sslplus', 'csr': 'fakecsr', 'validity': '1', 'common_name': 'fakeco.biz',
             'org_name': 'Fake Co', 'org_addr1': '123 Nowhere Lane', 'org_city': 'Nowhere',
             'org_state': 'UT', 'org_zip': '12345', 'org_country': 'US',
             'org_contact_firstname': 'William', 'org_contact_lastname': 'Billson',
             'org_contact_email': 'bbillson@fakeco.biz', 'org_contact_telephone': '2345556789',
             'server_type': '2', 'org_unit': 'FakeCo', 'sans': "['www.fakeco.biz', 'fake.co.uk']",
             'org_addr2': 'Infinitieth Floor', 'telephone': '2345556789',
             'org_contact_job_title': 'Janitor', 'org_contact_telephone_ext': '1001'}
        occ = self.get_occ(self._optionals_dict)
        payload = occ.get_params()
        self.assertTrue(len(payload) > 0)
        d = parse_qs(payload)
        for k in d.keys():
            self.assertEqual([actuals[k]], d[k])
        self.assertEqual(len(actuals), len(d))

    def test_get_headers(self):
        occ = self.get_occ(self._requireds_dict)
        self.assertEqual('application/x-www-form-urlencoded', occ.get_headers()['Content-Type'])
        self.assertEqual('application/json', occ.get_headers()['Accept'])

    def test_enumerate_certificate_types(self):
        certtypes = [certtype for certtype in CertificateType()]
        self.assertNotEqual(-1, certtypes.index(CertificateType.SSLPLUS))
        self.assertNotEqual(-1, certtypes.index(CertificateType.UC))
        self.assertNotEqual(-1, certtypes.index(CertificateType.EVMULTI))
        self.assertNotEqual(-1, certtypes.index(CertificateType.EVSSL))
        self.assertNotEqual(-1, certtypes.index(CertificateType.WILDCARD))

    def test_enumerate_validity(self):
        validities = [period for period in Validity()]
        self.assertNotEqual(-1, validities.index(Validity.ONE_YEAR))
        self.assertNotEqual(-1, validities.index(Validity.TWO_YEARS))
        self.assertNotEqual(-1, validities.index(Validity.THREE_YEARS))


if __name__ == '__main__':
   unittest.main()