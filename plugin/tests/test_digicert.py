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

        self.digicert_patcher = mock.patch(
            'barbican.plugin.dc._create_order'
        )
        self.digicert_patcher2 = mock.patch(
            'barbican.plugin.dc._get_order_status'
        )
        self.mock_create_order = self.digicert_patcher.start()
        self.mock_check_status = self.digicert_patcher2.start()

    def tearDown(self):
        super(WhenTestingDigicertPlugin, self).tearDown()
        if hasattr(self, 'mock_create_order'):
            self.mock_create_order.stop()
            self.mock_check_status.stop()

    def test_successful_issue_certificate_request(self):
        """ tests a successful order submission
        :return: dict is returned with the order id
        """
        self.mock_create_order.return_value = {'status_message': '12345'}

        order_id = '1234'
        plugin_meta = dict()

        result = self.digicert.issue_certificate_request(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "waiting for CA")

    def test_unsuccessful_certificate_request_can_retry(self):
        """ tests an unsuccessful order submission
        :return:
        """
        self.mock_create_order.return_value = {'retry_msec': 60}

        order_id = '1234'
        plugin_meta = dict()

        result = self.digicert.issue_certificate_request(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "client data issue seen")


    def test_check_order_status_pending(self):
        """ tests for an order with status pending
        :return:
        """
        self.mock_check_status.return_value = {'result': 'waiting for CA'}

        order_id = '12345'
        plugin_meta = dict()

        result = self.digicert.check_certificate_status(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "waiting for CA")

    def test_check_order_status_failed(self):
        self.mock_check_status.return_value = {'retry_msec': 60}

        order_id = '12345'
        plugin_meta = dict()

        result = self.digicert.check_certificate_status(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "client data issue seen")


    def test_check_order_status_issued(self):
        self.mock_check_status.return_value = {'certificate': 'certificate'}

        order_id = '12345'
        plugin_meta = dict()

        result = self.digicert.check_certificate_status(
            order_id,
            self.order_meta,
            plugin_meta
        )

        self.assertEqual(result.status, "certificate generated")

    def test_unsupported_modify(self):
        order_id = '1234'
        plugin_meta = dict()
        self.assertRaises(
            NotImplementedError,
            self.digicert.modify_certificate_request,
            order_id,
            self.order_meta,
            plugin_meta
        )
