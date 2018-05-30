# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from tests.unit import test
from xrally_docker.task.scenarios import networks


class ListNetworksTestCase(test.TestCase):

    def test_list(self):
        dclient = mock.MagicMock()
        dclient.list_networks.return_value = [
            {"Name": "foo", "Id": "id-1", "Driver": "driver-1"},
            {"Name": "bar", "Id": "id-2", "Driver": "driver-2"}]

        scenario = networks.ListNetworks({"docker": {}})
        scenario.client = dclient

        scenario.run()

        dclient.list_networks.assert_called_once_with(
            None, detailed=False, label=None, ntype=None
        )

        self.assertEqual([], scenario._output["additive"])
        self.assertEqual(
            [{
                "chart_plugin": "Table",
                "title": "Networks",
                "description": "A list of available networks.",
                "data": {
                    "cols": ["Name", "ID", "Driver"],
                    "rows": [["foo", "id-1", "driver-1"],
                             ["bar", "id-2", "driver-2"]]
                }
            }],
            scenario._output["complete"])

    def test_list_empty(self):
        dclient = mock.MagicMock()
        dclient.list_networks.return_value = []

        scenario = networks.ListNetworks({"docker": {}})
        scenario.client = dclient

        scenario.run()

        dclient.list_networks.assert_called_once_with(
            None, detailed=False, label=None, ntype=None
        )

        self.assertEqual([], scenario._output["additive"])
        self.assertEqual(
            [{
                "chart_plugin": "TextArea",
                "title": "Networks",
                "data": ["No networks are available."]}],
            scenario._output["complete"])


class CreateAndDeleteNetworkTestCase(test.TestCase):

    def test_run(self):
        dclient = mock.MagicMock()
        net = {"Name": "foo", "Id": "id"}
        dclient.create_network.return_value = net

        scenario = networks.CreateAndDeleteNetwork({"docker": {}})
        scenario.client = dclient

        scenario.run()

        dclient.create_network.assert_called_once_with(
            attachable=None, check_duplicate=None, driver=None,
            enable_ipv6=False, ingress=None, internal=False, ipam=None,
            labels=None, options=None, scope=None
        )
        dclient.delete_network.assert_called_once_with(
            net["Id"]
        )
