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

import copy

from xrally_docker.common.cleanup import manager
from xrally_docker.task import context


@context.configure("networks", order=100)
class NetworksContext(context.BaseDockerContext):
    """Create one or several docker networks."""

    CONFIG_SCHEMA = {
        "oneOf": [
            {
                "description": "Create a single network",
                "$ref": "#/definitions/single-network"
            },
            {
                "description": "Create several networks.",
                "type": "array",
                "minItems": 1,
                "items": {"$ref": "#/definitions/single-network"}
            }
        ],
        "definitions": {
            "ipam": {
                "type": "object",
                "description": "Custom IP scheme for the network",
                "properties": {
                    "Driver": {
                        "type": "string",
                        "description": "The name of the driver"},
                    "Config": {
                        "type": "array",
                        "description": "A list of IPAM Pool configurations.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "subnet": {
                                    "type": "string",
                                    "description": "Custom subnet for this "
                                                   "IPAM pool using the CIDR "
                                                   "notation."
                                },
                                "iprange": {
                                    "type": "string",
                                    "description": "Custom IP range for "
                                                   "endpoints in this IPAM "
                                                   "pool using the CIDR "
                                                   "notation."
                                },
                                "gateway": {
                                    "type": "string",
                                    "description": "Custom IP address for the"
                                                   " pool's gateway."
                                },
                                "aux_addresses": {
                                    "type": "object",
                                    "description":
                                        "A dictionary of ``key -> ip_address``"
                                        "relationships specifying auxiliary "
                                        "addresses that need to be allocated "
                                        "by the IPAM driver."
                                }
                            },
                            "additionalProperties": False
                        }
                    },
                    "Options": {
                        "type": "object",
                        "description": "Driver options.",
                        "additionalProperties": True
                    }
                },
                "additionalProperties": False,
                "required": ["Driver"]
            },
            "single-network": {
                "type": "object",
                "properties": {
                    "driver": {
                        "type": "string",
                        "description": "Name of the driver used to create "
                                       "the network"
                    },
                    "options": {
                        "type": "object",
                        "description": "Driver options."
                    },
                    "ipam": {"$ref": "#/definitions/ipam"},
                    "internal": {
                        "type": "boolean",
                        "description":
                            "Restrict external access to the network."
                    },
                    "labels": {
                        "type": "array",
                        "description": "A list of labels to apply to the "
                                       "network",
                        "items": {"type": "string",
                                  "description": "A label to apply."}
                    },
                    "enable_ipv6": {
                        "type": "boolean",
                        "description": "Enable IPv6 on the network."
                    },
                    "attachable": {
                        "type": "boolean",
                        "description": "If enabled, and the network is in the "
                                       "global scope,  non-service containers"
                                       " on worker nodes will be able to "
                                       "connect to the network."
                    },
                    "scope": {
                        "description": "The network's scope",
                        "enum": ["local", "global", "swarm"]},
                    "ingress": {
                        "type": "boolean",
                        "description": "If set, create an ingress network "
                                       "which provides the routing-mesh in "
                                       "swarm mode."}
                },
                "additionalProperties": False
            }
        }
    }

    def setup(self):
        self.context["docker"]["networks"] = []
        networks = self.config
        if isinstance(networks, dict):
            networks = [networks]

        for net_cfg in networks:
            net_cfg = copy.deepcopy(net_cfg)
            if "ipam" in net_cfg:
                net_cfg["ipam"].setdefault("Options", {})
            self.context["docker"]["networks"].append(
                self.client.create_network(**net_cfg))

    def cleanup(self):
        manager.cleanup(
            names=["network"],
            spec=self.context["env"]["platforms"]["docker"],
            superclass=self.__class__,
            owner_id=self.get_owner_id()
        )
