#!/usr/bin/env python

import unittest
import ssl

from ..https import verify_peer


class TestPeerVerifier(unittest.TestCase):
    test_cert_info = {
        'notAfter': 'Jan 01 12:00:00 2020 GMT',
        'subjectAltName': (
            ('DNS', 'www.example.com'),
            ('DNS', 'example.com'),
            ('DNS', 'www.subhost.example.com'),
            ('DNS', 'login.example.com')
        ),
        'subject': (
            (('businessCategory', 'Private Organization')),
            (('1.3.6.1.4.1.311.60.2.1.3', 'US')),
            (('1.3.6.1.4.1.311.60.2.1.2', 'Utah')),
            (('serialNumber', '1213145-9876')),
            (('streetAddress', '123 Nowhere Lane')),
            (('postalCode', '84321')),
            (('countryName', 'US')),
            (('stateOrProvinceName', 'Utah')),
            (('localityName', 'Nowhere')),
            (('organizationName', 'Example, Inc.')),
            (('commonName', 'www.example.com'))
        )
    }

    wildcard_cert_info = {
        'notAfter': 'Jan 01 12:00:00 2020 GMT',
        'subject': (
            (('businessCategory', 'Private Organization')),
            (('1.3.6.1.4.1.311.60.2.1.3', 'US')),
            (('1.3.6.1.4.1.311.60.2.1.2', 'Utah')),
            (('serialNumber', '1213145-9876')),
            (('streetAddress', '123 Nowhere Lane')),
            (('postalCode', '84321')),
            (('countryName', 'US')),
            (('stateOrProvinceName', 'Utah')),
            (('localityName', 'Nowhere')),
            (('organizationName', 'Example, Inc.')),
            (('commonName', '*.example.com'))
        )
    }

    partial_wildcard_cert_info = {
        'notAfter': 'Jan 01 12:00:00 2020 GMT',
        'subject': (
            (('businessCategory', 'Private Organization')),
            (('1.3.6.1.4.1.311.60.2.1.3', 'US')),
            (('1.3.6.1.4.1.311.60.2.1.2', 'Utah')),
            (('serialNumber', '1213145-9876')),
            (('streetAddress', '123 Nowhere Lane')),
            (('postalCode', '84321')),
            (('countryName', 'US')),
            (('stateOrProvinceName', 'Utah')),
            (('localityName', 'Nowhere')),
            (('organizationName', 'Example, Inc.')),
            (('commonName', 'log*.example.com'))
        )
    }

    wildcard_san_cert_info = {
        'notAfter': 'Jan 01 12:00:00 2020 GMT',
        'subjectAltName': (
            ('DNS', '*.example.com'),
        ),
        'subject': (
            (('businessCategory', 'Private Organization')),
            (('1.3.6.1.4.1.311.60.2.1.3', 'US')),
            (('1.3.6.1.4.1.311.60.2.1.2', 'Utah')),
            (('serialNumber', '1213145-9876')),
            (('streetAddress', '123 Nowhere Lane')),
            (('postalCode', '84321')),
            (('countryName', 'US')),
            (('stateOrProvinceName', 'Utah')),
            (('localityName', 'Nowhere')),
            (('organizationName', 'Example, Inc.')),
            (('commonName', 'www.example.com'))
        )
    }

    def test_common_name(self):
        try:
            verify_peer('www.example.com', self.test_cert_info)
        except ssl.SSLError as e:
            self.fail(e)

    def test_san(self):
        try:
            verify_peer('www.example.com', self.test_cert_info)
            verify_peer('example.com', self.test_cert_info)
            verify_peer('www.subhost.example.com', self.test_cert_info)
            verify_peer('login.example.com', self.test_cert_info)
        except ssl.SSLError as e:
            self.fail(e)

    def test_no_match(self):
        for host in ['ww.example.com', 'logout.example.com', 'www.exapmle.com', 'www.example.con']:
            try:
                verify_peer(host, self.test_cert_info)
                self.fail('Host "%s" matched' % host)
            except ssl.SSLError:
                pass

    def test_wildcard(self):
        try:
            verify_peer('www.example.com', self.wildcard_cert_info)
            verify_peer('login.example.com', self.wildcard_cert_info)
        except ssl.SSLError as e:
            self.fail(e)

    def test_wildcard_san(self):
        try:
            verify_peer('www.example.com', self.wildcard_san_cert_info)
            verify_peer('login.example.com', self.wildcard_san_cert_info)
        except ssl.SSLError as e:
            self.fail(e)

    def test_wildcard_dont_match_shorter_dns_name(self):
        try:
            verify_peer('example.com', self.wildcard_cert_info)
            self.fail('Wildcard "*.example.com" matched "example.com"')
        except ssl.SSLError:
            pass
        try:
            verify_peer('example.com', self.wildcard_san_cert_info)
            self.fail('Wildcard "*.example.com" matched "example.com"')
        except ssl.SSLError:
            pass

    def test_wildcard_dont_match_longer_dns_name(self):
        try:
            verify_peer('www.subhost.example.com', self.wildcard_cert_info)
            self.fail('Wildcard "*.example.com" matched "www.subhost.example.com"')
        except ssl.SSLError:
            pass
        try:
            verify_peer('www.subhost.example.com', self.wildcard_san_cert_info)
            self.fail('Wildcard "*.example.com" matched "www.subhost.example.com"')
        except ssl.SSLError:
            pass

    def test_wildcard_matches_partial_on_lhs_component(self):
        try:
            verify_peer('login.example.com', self.partial_wildcard_cert_info)
            verify_peer('logout.example.com', self.partial_wildcard_cert_info)
        except ssl.SSLError as e:
            self.fail(e)

if __name__ == '__main__':
    unittest.main()