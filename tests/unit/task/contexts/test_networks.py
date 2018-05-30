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

import docker
import mock

from tests.unit import test
from xrally_docker.task.contexts import networks


class NetworksContextTestCase(test.TestCase):

    def setUp(self):
        super(NetworksContextTestCase, self).setUp()
        self.owner_id = "foo-bar"
        self.ctx = {
            "env": {"platforms": {"docker": {}}},
            "owner_id": self.owner_id,
            "config": {"networks@docker": {}}
        }
        with mock.patch.object(docker, "DockerClient"):
            self.ctx_obj = networks.NetworksContext(self.ctx)
        self.docker = mock.MagicMock()
        self.ctx_obj.client = self.docker

    def test_setup(self):
        self.ctx_obj.setup()

        self.assertEqual(self.ctx["docker"]["networks"],
                         [self.docker.create_network.return_value])

        self.docker.create_network.assert_called_once_with()

    @mock.patch("xrally_docker.task.contexts.networks.manager")
    def test_cleanup(self, mock_manager):
        self.ctx_obj.cleanup()

        mock_manager.cleanup.assert_called_once_with(
            names=["network"],
            spec=self.ctx["env"]["platforms"]["docker"],
            superclass=networks.NetworksContext,
            owner_id=self.owner_id
        )
