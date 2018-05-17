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
from xrally_docker.task.contexts import images


class ImagesContextTestCase(test.TestCase):

    def setUp(self):
        super(ImagesContextTestCase, self).setUp()
        self.owner_id = "foo-bar"
        self.ctx = {
            "env": {"platforms": {"docker": {}}},
            "owner_id": self.owner_id,
            "config": {"images@docker": {}}
        }
        with mock.patch.object(docker, "DockerClient"):
            self.ctx_obj = images.ImagesContext(self.ctx)
        self.docker = mock.MagicMock()
        self.ctx_obj.client = self.docker

    def test_setup(self):
        image_objs = [mock.MagicMock(), mock.MagicMock()]
        self.docker.list_images.return_value = image_objs

        # Case #1: Names are not specified, so only existing images should be
        #   listed by default
        self.ctx_obj.setup()

        self.assertFalse(self.docker.pull_image.called)
        self.assertEqual(image_objs, self.ctx["docker"]["images"])

        # Case #2: Names are specified, so the new image should be pulled.
        #   Existing images should not be listed by default in such case
        del self.ctx["docker"]["images"]
        self.docker.list_images.reset_mock()
        self.ctx_obj.config = {"names": ["foo"]}

        self.ctx_obj.setup()

        self.assertFalse(self.docker.list_images.called)
        self.assertEqual([self.docker.pull_image.return_value],
                         self.ctx["docker"]["images"])

        # Case #3: Names are specified + existing images flag is also present.
        del self.ctx["docker"]["images"]
        self.docker.list_images.reset_mock()
        self.ctx_obj.config = {"names": ["foo"], "existing": True}

        self.ctx_obj.setup()

        expected_images = set(image_objs)
        expected_images.add(self.docker.pull_image.return_value)
        self.assertEqual(expected_images, set(self.ctx["docker"]["images"]))

    @mock.patch("xrally_docker.task.contexts.images.manager")
    def test_cleanup(self, mock_manager):
        self.ctx_obj.cleanup()

        mock_manager.cleanup.assert_called_once_with(
            names=["image"],
            spec=self.ctx["env"]["platforms"]["docker"],
            superclass=images.ImagesContext,
            owner_id=self.owner_id
        )
