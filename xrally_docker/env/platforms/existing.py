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

from xrally_docker import service


LOG = logging.getLogger(__name__)

CONF = cfg.CONF


@platform.configure(name="existing", platform="docker")
class Docker(platform.Platform):
    """Default plugin for Docker."""

    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "host": {
                "type": "string",
                "description": "The URL to the Docker host"},
            "timeout": {
                "type": "number",
                "minimum": 0,
                "description": "Default timeout for API calls, in seconds."},
            "tls_verify": {
                "type": "boolean",
                "description": "Verify the host against a CA certificate."},
            "cert_path": {
                "type": "string",
                "description":
                    "A path to a directory containing TLS certificates to use "
                    "when connecting to the Docker host."},
            "version": {
                "type": "string",
                "description":
                    "The version of the API to use. Defaults to ``auto`` which"
                    "means automatically detection of the server's version."
            },
            "ssl_version": {
                "type": "integer",
                "description":
                    "A valid SSL version (see "
                    "https://docs.python.org/3.5/library/ssl.html"
                    "#ssl.PROTOCOL_TLSv1)"
            }
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
            service.Docker(self.platform_data).get_info()
        except Exception:
            return {
                "available": False,
                "message": "Something went wrong",
                "traceback": traceback.format_exc()
            }

        return {"available": True}

    def info(self):
        """Return an info about Docker server."""
        return {"info": service.Docker(self.platform_data).get_info()}

    def _get_validation_context(self):
        return {}

    @classmethod
    def create_spec_from_sys_environ(cls, sys_environ):
        """Create a spec based on system environment.

        The environment variables used are the same as those used by the
        Docker command-line client. They are:

        .. envvar:: DOCKER_HOST

            The URL to the Docker host.

        .. envvar:: DOCKER_TLS_VERIFY

            Verify the host against a CA certificate.

        .. envvar:: DOCKER_CERT_PATH

            A path to a directory containing TLS certificates to use when
            connecting to the Docker host.

        This is an adopted version of `docker.utils.kwargs_from_env`.
        """
        spec = {}
        host = sys_environ.get("DOCKER_HOST")
        if host:
            spec["host"] = host
        cert_path = sys_environ.get("DOCKER_CERT_PATH") or None
        if cert_path:
            spec["cert_path"] = cert_path

        # empty string for tls verify counts as "false".
        # Any value or 'unset' counts as true.
        tls_verify = sys_environ.get("DOCKER_TLS_VERIFY")
        if tls_verify == "":
            tls_verify = False
        else:
            tls_verify = tls_verify is not None
        spec["tls_verify"] = tls_verify

        enable_tls = cert_path or spec["tls_verify"]

        if not enable_tls:
            return {"available": True, "spec": spec}

        if not cert_path:
            spec["cert_path"] = os.path.join(
                os.path.expanduser("~"), ".docker")

        return {"available": True, "spec": spec}
