#!/usr/bin/env python

import unittest
from urlparse import parse_qs
from digicert import Org, OrgAddress, OrgContact
from digicert.api.commands import OrderCertificateCommand
from tests import MockConnection


class TestOrderCertificateCommand(unittest.TestCase):
    _customer_name = '12345'
    _customer_api_key = 'abapsdrtaewrh89249sbs89as0d'
    _api_host = 'www.digicert.com'
    _api_path = '/clients/retail/api/?action=order_certificate'
    _org_addr = OrgAddress('123 Nowhere Lane', 'Nowhere', 'UT', '12345', 'US')
    _org_oaddr = OrgAddress('123 Nowhere Lane', 'Nowhere', 'UT', '12345', 'US',
                            addr2='Infinitieth Floor', telephone='2345556789')
    _org_contact = OrgContact('Bill', 'Billson', 'bbillson@fakeco.biz', '2345556789')
    _org_ocontact = OrgContact('Bill', 'Billson', 'bbillson@fakeco.biz', '2345556789',
                               job_title='CTO', telephone_ext='5150')
    _org = Org('Fake Co.', _org_addr, _org_contact)
    _requireds_dict = {
        'certificate_type': 'sslplus',
        'csr': 'fakecsr',
        'validity': '1',
        'common_name': 'fake.com',
        'org': _org}
    _optionals_dict = {
        'certificate_type': 'sslplus',
        'csr': 'fakecsr',
        'validity': '1',
        'common_name': 'fake.com',
        'org': Org('Fake Co.', _org_oaddr, _org_ocontact),
        'server_type': '2',
        'org_unit': 'FakeCo',
        'sans': 'fakeco.biz, fake.co.uk'}

    def validate(self, o):
        self.assertEqual(o.customer_name, '12345')
        self.assertEqual(o.customer_api_key, 'abapsdrtaewrh89249sbs89as0d')
        self.assertEqual(o.response_type, 'json')
        self.assertEqual(o.certificate_type, 'sslplus')
        self.assertEqual(o.csr, 'fakecsr')
        self.assertEqual(o.validity, 1)
        self.assertEqual(o.common_name, 'fake.com')
        self.assertEqual(o.org_name, 'Fake Co.')
        self.assertEqual(o.org_addr1, '123 Nowhere Lane')
        self.assertEqual(o.org_city, 'Nowhere')
        self.assertEqual(o.org_state, 'UT')
        self.assertEqual(o.org_zip, '12345')
        self.assertEqual(o.org_country, 'US')
        self.assertEqual(o.org_contact_firstname, 'Bill')
        self.assertEqual(o.org_contact_lastname, 'Billson')
        self.assertEqual(o.org_contact_email, 'bbillson@fakeco.biz')
        self.assertEquals(o.org_contact_telephone, '2345556789')

    def validate_opt(self, o):
        self.assertEqual(o.server_type, 2)
        self.assertEqual(o.org_unit, 'FakeCo')
        self.assertEqual(o.sans, 'fakeco.biz, fake.co.uk')
        self.assertEqual(o.org_addr2, 'Infinitieth Floor')
        self.assertEqual(o.telephone, '2345556789')
        self.assertEqual(o.org_contact_job_title, 'CTO')
        self.assertEqual(o.org_contact_telephone_ext, '5150')

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
        self.assertEqual('MTIzNDU6YWJhcHNkcnRhZXdyaDg5MjQ5c2JzODlhczBk', occ.get_authorization())

    def test_get_payload(self):
        actuals = {'customer_api_key': self._customer_api_key, 'customer_name': self._customer_name,
             'certificate_type': 'sslplus', 'csr': 'fakecsr', 'validity': '1', 'common_name': 'fake.com',
             'org_name': 'Fake Co.', 'org_addr1': '123 Nowhere Lane', 'org_city': 'Nowhere',
             'org_state': 'UT', 'org_zip': '12345', 'org_country': 'US',
             'org_contact_firstname': 'Bill', 'org_contact_lastname': 'Billson',
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
             'certificate_type': 'sslplus', 'csr': 'fakecsr', 'validity': '1', 'common_name': 'fake.com',
             'org_name': 'Fake Co.', 'org_addr1': '123 Nowhere Lane', 'org_city': 'Nowhere',
             'org_state': 'UT', 'org_zip': '12345', 'org_country': 'US',
             'org_contact_firstname': 'Bill', 'org_contact_lastname': 'Billson',
             'org_contact_email': 'bbillson@fakeco.biz', 'org_contact_telephone': '2345556789',
             'server_type': '2', 'org_unit': 'FakeCo', 'sans': 'fakeco.biz, fake.co.uk',
             'org_addr2': 'Infinitieth Floor', 'telephone': '2345556789',
             'org_contact_job_title': 'CTO', 'org_contact_telephone_ext': '5150'}
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

    def test_send(self):
        occ = self.get_occ(self._requireds_dict)
        mc = MockConnection(self._api_host)
        occ.send(conn=mc)
        self.assertEqual(self._api_host, mc.host)
        self.assertEqual(self._api_path, mc.path)
        self.assertEqual('POST', mc.method)
        self.assertEqual(occ.get_params(), mc.params)
        self.assertEqual(occ.get_headers(), mc.headers)


if __name__ == '__main__':
   unittest.main()