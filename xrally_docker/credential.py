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

from rally import consts
from rally.deployment import credential

from xrally_docker import client


@credential.configure("docker")
class DockerCredential(credential.Credential):
    """Credential for Docker."""

    def __init__(self, host=None, tls_verify=None, cert_path=None,
                 permission=None):
        enable_tls = cert_path or tls_verify
        self.host = host.replace("tcp://", "https://") if enable_tls else host
        self.tls_verify = tls_verify
        self.cert_path = cert_path
        if enable_tls and not self.cert_path:
            self.cert_path = os.path.join(os.path.expanduser("~"), ".docker")
        self.permission = permission
        self._clients_cache = {}

    def to_dict(self):
        return {"host": self.host,
                "tls_verify": self.tls_verify,
                "cert_path": self.cert_path,
                "permission": self.permission}

    def verify_connection(self):
        self.clients().verify_connection()

    def list_services(self):
        return [{"name": "docker", "version": self.clients().version()}]

    def clients(self, api_info=None):
        return client.DockerClient(self)


@credential.configure_builder("docker")
class DockerCredentialBuilder(credential.CredentialBuilder):
    """Builds docker credentials provided by ExistingCloud config."""

    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "host": {"type": "string",
                     "description": "The URL to the Docker host"},
            "tls_verify": {
                "type": "boolean",
                "description": "Verify the host against a CA certificate."},
            "cert_path": {"type": "string",
                          "description": "A path to a directory containing TLS"
                                         " certificates to use when connecting"
                                         " to the Docker host."}
        },
        "additionalProperties": False
    }

    def build_credentials(self):
        return {
            "admin": DockerCredential(
                host=self.config.get("host"),
                tls_verify=self.config.get("tls_verify"),
                cert_path=self.config.get("cert_path"),
                permission=consts.EndpointPermission.ADMIN).to_dict(),
            "users": []}
