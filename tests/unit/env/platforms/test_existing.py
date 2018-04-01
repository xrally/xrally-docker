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

import os

from tests.unit import test
from xrally_docker.env.platforms import existing


class DockerPlatformTestCase(test.TestCase):

    def test_create_spec_from_sys_environ(self):
        self.assertEqual(
            {"available": True, "spec": {"tls_verify": False}},
            existing.Docker.create_spec_from_sys_environ({}))

        self.assertEqual(
            {"available": True, "spec": {"tls_verify": False,
                                         "cert_path": "/foo",
                                         "host": "localhost"}},
            existing.Docker.create_spec_from_sys_environ(
                {"DOCKER_HOST": "localhost",
                 "DOCKER_CERT_PATH": "/foo"}))

        self.assertEqual(
            {
                "available": True,
                "spec": {"tls_verify": True,
                         "cert_path": os.path.join(
                             os.path.expanduser("~"), ".docker"),
                         "host": "localhost"}},
            existing.Docker.create_spec_from_sys_environ(
                {"DOCKER_HOST": "localhost",
                 "DOCKER_TLS_VERIFY": True}))
