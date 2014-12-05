# Copyright (c) 2013-2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import testtools

try:
    import barbican.plugin.dc as dc
    imports_ok = True
except ImportError:
    # Digicert imports probably not available
    imports_ok = False

from barbican.tests import utils


@testtools.skipIf(not imports_ok, "Digicert imports not available")
class WhenTestingDigicertPlugin(utils.BaseTestCase):

    def setUp(self):
        super(WhenTestingDigicertPlugin, self).setUp()
        self.order_meta = {
            'cert_type': 'sslplus',
            'organization': 'My Org',
            'phone': '555-555-5555',
            'validity': '1',
            'common_name': 'fake.com',
            'org_name': 'Fake Co.',
            'org_addr1': '123 Nowhere Lane',
            'org_city': 'Nowhere',
            'org_state': 'UT',
            'org_zip': '12345',
            'org_country': 'US',
            'org_contact_firstname': 'Bill',
            'org_contact_lastname': 'Billson',
            'org_contact_email': 'bbillson@fakeco.biz',
            'org_contact_telephone': '2345556789',
            'csr': 'this is a fake csr'
        }

        self.error_msg = 'Error Message Here'
        self.conf_mock = mock.MagicMock(account_id='93431234',
                                        api_key='abcdefghij',
                                        dc_host='www.apidomain.com')
        self.digicert = dc.DigiCertCertificatePlugin(conf=self.conf_mock)
        self.digicert.orderclient = mock.MagicMock()

    def tearDown(self):
        super(WhenTestingDigicertPlugin, self).tearDown()
        if hasattr(self, 'mock_create_order'):
            pass
            # self.mock_create_order.stop()
            # self.mock_check_status.stop()

    def test_successful_issue_certificate_request(self):
        """tests a successful order submission

        :return: dict is returned with the order id
        """

        self.digicert.orderclient.place.return_value = {'id': '123456'}

        order_id = '1234'
        plugin_meta = dict()

        result = self.digicert.issue_certificate_request(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "waiting for CA")

    def test_no_api_key(self):
        """tests validation for no api key passed in

        :return:
        """
        bad_conf_mock = mock.MagicMock()
        bad_conf_mock.digicert_plugin.api_key = None
        bad_conf_mock.digicert_plugin.account_id = '93431234'
        bad_conf_mock.digicert_plugin.dc_host = 'www.apidomain.com'
        self.assertRaises(
            ValueError,
            dc.DigiCertCertificatePlugin,
            bad_conf_mock
        )

    def test_no_dc_host(self):
        """test validation for no host url passed in

        :return:
        """
        bad_conf_mock = mock.MagicMock()
        bad_conf_mock.digicert_plugin.api_key = 'abcdefghijklmnopqrstuvwxyz'
        bad_conf_mock.digicert_plugin.account_id = '34783921'
        bad_conf_mock.digicert_plugin.dc_host = None
        self.assertRaises(
            ValueError,
            dc.DigiCertCertificatePlugin,
            bad_conf_mock
        )

    def test_unsuccessful_certificate_request_can_retry(self):
        """tests an unsuccessful order submission

        :return:
        """

        self.digicert.orderclient.place.return_value = {}

        order_id = '1234'
        plugin_meta = dict()

        result = self.digicert.issue_certificate_request(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "CA unavailable for request")

    def test_check_order_status_pending(self):
        """test for an order with status pending

        :return:
        """

        self.digicert.orderclient.view.return_value = {
            'status': 'pending issuance'}

        order_id = '12345'
        plugin_meta = dict()

        result = self.digicert.check_certificate_status(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "waiting for CA")

    def test_check_order_status_failed(self):
        """test for an order that fails from client API

        :return:
        """

        self.digicert.orderclient.view.return_value = {}

        order_id = '12345'
        plugin_meta = dict()

        result = self.digicert.check_certificate_status(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "client data issue seen")

    def test_check_order_status_issued(self):
        """test to view order status when cert is issued

        :return:
        """

        self.digicert.orderclient.view.return_value = {
            'status': 'issued'}

        order_id = '12345'
        plugin_meta = dict()

        result = self.digicert.check_certificate_status(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "certificate generated")

    def test_unsupported_modify(self):
        """exercising modify cert request method

        :return:
        """
        order_id = '1234'
        plugin_meta = dict()
        self.assertRaises(
            NotImplementedError,
            self.digicert.modify_certificate_request,
            order_id,
            self.order_meta,
            plugin_meta
        )

    def test_unsupported_cancel(self):
        """exercising cancel cert request method

        :return:
        """
        order_id = '1234'
        plugin_meta = dict()
        self.assertRaises(
            NotImplementedError,
            self.digicert.cancel_certificate_request,
            order_id,
            self.order_meta,
            plugin_meta
        )

    def test_supports(self):
        """exercising supports method

        :return:
        """
        self.assertTrue(self.digicert.supports(dict()))
