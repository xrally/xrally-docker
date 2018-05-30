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

from xrally_docker.task import scenario
from xrally_docker.task import validators


@scenario.configure("Docker.list_networks")
class ListNetworks(scenario.BaseDockerScenario):

    def run(self, driver=None, label=None, ntype=None, detailed=False):
        """List docker networks

        :param driver: a network driver to match
        :param label: label to match
        :param ntype: Filters networks by type.
        :param detailed: Grep detailed information about networks (aka greedy)
        """
        networks = self.client.list_networks(
            driver, label=label, ntype=ntype, detailed=detailed)
        if networks:
            self.add_output(
                complete={
                    "title": "Networks",
                    "description": "A list of available networks.",
                    "chart_plugin": "Table",
                    "data": {
                        "cols": ["Name", "ID", "Driver"],
                        "rows": [[n["Name"], n["Id"], n["Driver"]]
                                 for n in networks]
                    }
                }
            )
        else:
            self.add_output(complete={"title": "Networks",
                                      "chart_plugin": "TextArea",
                                      "data": ["No networks are available."]})


@validators.add("enum", param_name="scope", missed=True,
                values=["local", "global", "swarm"])
@scenario.configure(
    "Docker.create_and_delete_network",
    context={"cleanup@docker": ["network"]})
class CreateAndDeleteNetwork(scenario.BaseDockerScenario):

    def run(self, driver=None, options=None, ipam=None,
            check_duplicate=None, internal=False, labels=None,
            enable_ipv6=False, attachable=None, scope=None,
            ingress=None):
        """Create and delete docker network

        :param driver: Name of the driver used to create the network
        :param options: Driver options as a key-value dictionary
        :param ipam: Optional custom IP scheme for the network.
        :param check_duplicate: Request daemon to check for networks with
            same name.
        :param internal: Restrict external access to the network.
        :param labels: Map of labels to set on the network.
        :param enable_ipv6: Enable IPv6 on the network.
        :param attachable: If enabled, and the network is in the global
            scope,  non-service containers on worker nodes will be able to
            connect to the network.
        :param scope: Specify the network's scope (``local``, ``global`` or
            ``swarm``)
        :param ingress: If set, create an ingress network which provides
            the routing-mesh in swarm mode.
        """

        network = self.client.create_network(
            driver=driver,
            options=options,
            ipam=ipam,
            check_duplicate=check_duplicate,
            internal=internal,
            labels=labels,
            enable_ipv6=enable_ipv6,
            attachable=attachable,
            scope=scope,
            ingress=ingress)

        self.client.delete_network(network["Id"])
