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


class DockerClient(object):
    def __init__(self, credential):
        self.credential = credential
        self._client = None

    def __call__(self):
        if not self._client:
            # TODO(andreykurilin): use credentials
            self._client = docker.DockerClient.from_env()
        return self._client

    def verify_connection(self):
        self().version()

    def version(self):
        return self().version()["Version"]
