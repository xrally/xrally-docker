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
import traceback

from rally.common import cfg
from rally.common import logging
from rally.env import platform

from xrally_docker import client


LOG = logging.getLogger(__name__)

CONF = cfg.CONF


@platform.configure(name="existing", platform="docker")
class Docker(platform.Platform):
    """Default plugin for Docker."""

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

    def create(self):
        """Converts creds of Docker to internal presentation."""

        host = self.spec.get("host")
        enable_tls = self.spec.get("cert_path") or self.spec.get("tls_verify")
        if host:
            host = host.replace("tcp://", "https://") if enable_tls else host

        cert_path = self.spec.get("cert_path")
        if enable_tls and not cert_path:
            cert_path = os.path.join(os.path.expanduser("~"), ".docker")

        return {"host": host,
                "tls_verify": self.spec.get("tls_verify"),
                "cert_path": cert_path}, {}

    def destroy(self):
        # NOTE(boris-42): No action need to be performed.
        pass

    def cleanup(self, task_uuid=None):
        return {
            "message": "Coming soon!",
            "discovered": 0,
            "deleted": 0,
            "failed": 0,
            "resources": {},
            "errors": []
        }

    def check_health(self):
        """Check whatever platform is alive."""
        try:
            client.DockerClient(self.platform_data).verify_connection()
        except Exception:
            return {
                "available": False,
                "message": "Something went wrong",
                "traceback": traceback.format_exc()
            }

        return {"available": True}

    def info(self):
        """Return a version of a Docker."""
        return {
            "info": {
                "version": client.DockerClient(self.platform_data).version()
            }
        }

    def _get_validation_context(self):
        return {}

    @classmethod
    def create_spec_from_sys_environ(cls, sys_environ):
        # TODO(andreykurilin): make it work someday
        return platform.Platform.create_spec_from_sys_environ(sys_environ)
