#!/usr/bin/env python

import unittest
import json
from urlparse import parse_qs

from .. import CertificateType, Validity
from ..api.commands.v1 import OrderCertificateCommand as OrderCertificateCommandV1
from ..api.commands.v2 import OrderCertificateCommand as OrderCertificateCommandV2


class TestOrderCertificateCommand(object):
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
        raise NotImplementedError

    def validate_opt(self, o):
        self.assertEqual(o.server_type, 2)
        self.assertEqual(o.org_unit, 'FakeCo')
        self.assertEqual(o.sans, ['www.fakeco.biz', 'fake.co.uk'])
        self.assertEqual(o.org_addr2, 'Infinitieth Floor')
        self.assertEqual(o.telephone, '2345556789')
        self.assertEqual(o.org_contact_job_title, 'Janitor')
        self.assertEqual(o.org_contact_telephone_ext, '1001')

    def get_occ(self, additional_args):
        raise NotImplementedError

    def get_actuals(self):
        raise NotImplementedError

    def params_to_dict(self, params):
        raise NotImplementedError

    def verify_payload(self, actuals, params):
        raise NotImplementedError

    def test_get_headers(self):
        raise NotImplementedError

    def test_construct(self):
        self.validate(self.get_occ(self._requireds_dict))

    def test_construct_optionals(self):
        occ = self.get_occ(self._optionals_dict)
        self.validate(occ)
        self.validate_opt(occ)

    def test_get_payload(self):
        actuals = self.get_actuals()
        occ = self.get_occ(self._requireds_dict)
        self.verify_payload(actuals, occ.get_params())

    def test_get_payload_optionals(self):
        actuals = dict(self.get_actuals().items() +
                       {'server_type': '2', 'org_unit': 'FakeCo', 'sans': "['www.fakeco.biz', 'fake.co.uk']",
                        'org_addr2': 'Infinitieth Floor', 'telephone': '2345556789',
                        'org_contact_job_title': 'Janitor', 'org_contact_telephone_ext': '1001'}.items())
        occ = self.get_occ(self._optionals_dict)
        self.verify_payload(actuals, occ.get_params())

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


class TestOrderCertificateCommandV1(TestOrderCertificateCommand, unittest.TestCase):
    def get_occ(self, additional_args):
        return OrderCertificateCommandV1(customer_name=self._customer_name,
                                         customer_api_key=self._customer_api_key,
                                         **additional_args)

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
        self.assertEqual(o.org_contact_telephone, '2345556789')

    def test_get_auth(self):
        occ = self.get_occ(self._requireds_dict)
        self.assertEqual('MTIzNDU6YWJhcHNkcnRhZXdyaDg5MjQ5c2JzODlhczBk', occ.get_headers()['Authorization'])

    def get_actuals(self):
        return {'customer_api_key': self._customer_api_key, 'customer_name': self._customer_name,
                'certificate_type': 'sslplus', 'csr': 'fakecsr', 'validity': '1', 'common_name': 'fakeco.biz',
                'org_name': 'Fake Co', 'org_addr1': '123 Nowhere Lane', 'org_city': 'Nowhere',
                'org_state': 'UT', 'org_zip': '12345', 'org_country': 'US',
                'org_contact_firstname': 'William', 'org_contact_lastname': 'Billson',
                'org_contact_email': 'bbillson@fakeco.biz', 'org_contact_telephone': '2345556789'}

    def params_to_dict(self, params):
        return parse_qs(params)

    def verify_payload(self, actuals, payload):
        self.assertTrue(len(payload) > 0)
        d = self.params_to_dict(payload)
        for k in d.keys():
            self.assertEqual([actuals[k]], d[k], 'Nonmatching values for key %s' % k)
        self.assertEqual(len(actuals), len(d))

    def test_get_headers(self):
        occ = self.get_occ(self._requireds_dict)
        self.assertEqual('application/x-www-form-urlencoded', occ.get_headers()['Content-Type'])
        self.assertEqual('application/json', occ.get_headers()['Accept'])


class TestOrderCertificateCommandV2(TestOrderCertificateCommand, unittest.TestCase):
    def get_occ(self, additional_args):
        additional_args['organization_id'] = '654321'
        return OrderCertificateCommandV2(customer_api_key=self._customer_api_key,
                                         **additional_args)

    def validate(self, o):
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
        self.assertEqual(o.org_contact_telephone, '2345556789')
        self.assertEqual(o.organization_id, '654321')

    def test_get_auth(self):
        occ = self.get_occ(self._requireds_dict)
        self.assertEqual('abapsdrtaewrh89249sbs89as0d', occ.get_headers()['X-DC-DEVKEY'])

    def get_actuals(self):
        return {'customer_api_key': self._customer_api_key, 'organization_id': '654321',
                'certificate_type': 'sslplus', 'csr': 'fakecsr', 'validity': 1, 'common_name': 'fakeco.biz',
                'org_name': 'Fake Co', 'org_addr1': '123 Nowhere Lane', 'org_city': 'Nowhere',
                'org_state': 'UT', 'org_zip': '12345', 'org_country': 'US',
                'org_contact_firstname': 'William', 'org_contact_lastname': 'Billson',
                'org_contact_email': 'bbillson@fakeco.biz', 'org_contact_telephone': '2345556789'}

    def params_to_dict(self, params):
        return json.loads(params)

    def verify_payload(self, actuals, payload):
        self.assertTrue(len(payload) > 0)
        d = json.loads(payload)
        actuals['certificate'] = {
            'common_name': d['common_name'],
            'csr': d['csr'],
            'organization_units': [] if not 'organization_units' in d else d['organization_units'],
            'server_platform': {'id': -1} if not 'server_platform' in d else {'id': d['server_platform']},
            'signature_hash': 'sha256' if not 'signature_hash' in d else d['signature_hash'],
        }
        actuals['organization'] = {'id': d['organization_id']}
        actuals['validity_years'] = '1'
        if 'server_type' in d:
            actuals['server_type'] = d['server_type']

        for k in d.keys():
            if k != 'sans':
                self.assertEqual(actuals[k], d[k], 'Nonmatching values for key %s' % k)
        if 'sans' in d:
            for san in d['sans']:
                self.assertTrue(san in actuals['sans'])
        self.assertEqual(len(actuals), len(d))

    def test_get_headers(self):
        occ = self.get_occ(self._requireds_dict)
        self.assertEqual('application/json', occ.get_headers()['Content-Type'])
        self.assertEqual('application/json', occ.get_headers()['Accept'])


if __name__ == '__main__':
   unittest.main()