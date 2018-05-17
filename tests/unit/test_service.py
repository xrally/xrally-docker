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
from xrally_docker import service


class DockerServiceTestCase(test.TestCase):

    def setUp(self):
        super(DockerServiceTestCase, self).setUp()
        import docker

        p_mock_client = mock.patch.object(docker, "DockerClient")
        self.client_cls = p_mock_client.start()
        self.client = self.client_cls.return_value

        self.addCleanup(p_mock_client.stop)

        self.name_generator = mock.MagicMock()
        self.docker = service.Docker({}, name_generator=self.name_generator)

    def test___init___without_tls(self):
        # setUp method called it
        self.client_cls.reset_mock()

        from docker import tls

        p_mock_tls = mock.patch.object(tls, "TLSConfig")
        mock_tls = p_mock_tls.start()
        self.addCleanup(p_mock_tls.stop)

        spec = {}

        service.Docker(spec)

        self.assertFalse(mock_tls.called)
        self.client_cls.assert_called_once_with(
            base_url=None,
            timeout=60,
            tls=False, version='auto')

    def test___init___with_tls(self):
        # setUp method called it
        self.client_cls.reset_mock()

        from docker import tls

        p_mock_tls = mock.patch.object(tls, "TLSConfig")
        mock_tls = p_mock_tls.start()
        self.addCleanup(p_mock_tls.stop)

        timeout = 1
        spec = {
            "tls_verify": True,
            "cert_path": "/foo",
            "host": "localhost",
            "timeout": timeout}

        service.Docker(spec)

        mock_tls.assert_called_once_with(
            assert_hostname=False,
            ca_cert="/foo/ca.pem",
            client_cert=("/foo/cert.pem", "/foo/key.pem"),
            ssl_version=None,
            verify=True
        )
        self.client_cls.assert_called_once_with(
            base_url="localhost",
            timeout=timeout, tls=mock_tls.return_value,
            version="auto"
        )

    def test_get_info(self):
        self.client.version.return_value = {"Version": 3}

        self.assertEqual(self.client.version.return_value,
                         self.docker.get_info())

        self.client.version.assert_called_once_with()

    def test__fix_the_name(self):
        self.assertEqual("foo:bar", self.docker._fix_the_name("foo:bar"))
        self.assertEqual("foo:latest", self.docker._fix_the_name("foo"))

    def test_pull_image(self):
        image_obj = self.client.images.get.return_value
        image_name = "foo:bar"

        image = self.docker.pull_image(image_name)
        self.assertNotEqual(
            self.client.images.pull.return_value.attrs, image)
        self.assertEqual(image_obj.attrs, image)

        self.client.images.pull.assert_called_once_with(image_name)
        image_obj.tag.assert_called_once_with("foo",
                                              self.name_generator.return_value)

    def test_tag_image(self):
        image_obj = self.client.images.get.return_value
        image_name = "foo:bar"
        tags = ["xxx", "yyy"]

        image = self.docker.tag_image(image_name, tags=tags)
        self.assertEqual(image_obj.attrs, image)
        self.assertEqual(
            [mock.call("foo", t) for t in tags],
            image_obj.tag.call_args_list
        )

        image_obj.tag.reset_mock()
        self.docker.tag_image(image_name)
        image_obj.tag.assert_called_once_with(
            "foo", self.name_generator.return_value)
