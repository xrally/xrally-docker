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

from rally.task import atomic
from rally.task import service


class Docker(service.Service):
    def __init__(self, spec, name_generator=None, atomic_inst=None):
        super(Docker, self).__init__(None, name_generator=name_generator,
                                     atomic_inst=atomic_inst)
        self._spec = spec

        cert_path = self._spec.get("cert_path")
        tls_verify = self._spec.get("tls_verify", False)
        enable_tls = cert_path or tls_verify
        if enable_tls:
            from docker import tls as docker_tls

            tls = docker_tls.TLSConfig(
                client_cert=(os.path.join(cert_path, "cert.pem"),
                             os.path.join(cert_path, "key.pem")),
                ca_cert=os.path.join(cert_path, "ca.pem"),
                verify=tls_verify,
                ssl_version=self._spec.get("ssl_version"),
                assert_hostname=False)
        else:
            tls = False

        import docker

        self._client = docker.DockerClient(
            base_url=self._spec.get("host"),
            version=self._spec.get("version", "auto"),
            timeout=self._spec.get(
                "timeout", docker.constants.DEFAULT_TIMEOUT_SECONDS),
            tls=tls)

    @atomic.action_timer("docker.version")
    def get_info(self):
        """Get info about Docker server."""
        return self._client.version()

    @staticmethod
    def _fix_the_name(name):
        """Add 'latest' tag if no tag in the name."""
        if ":" not in name:
            return "%s:latest" % name
        return name

    @atomic.action_timer("docker.pull_image")
    def pull_image(self, name):
        """Pull the image by name.

        It there is no tag in the name, only the latest tag will be pulled.
        """
        image = self._client.images.pull(self._fix_the_name(name))
        if self._name_generator is not None:
            # add Rally tag.
            return self.tag_image(name)

        return image.attrs

    @atomic.action_timer("docker.get_image")
    def _get_image(self, name):
        """Get raw image object."""
        return self._client.images.get(self._fix_the_name(name))

    @atomic.action_timer("docker.get_image")
    def get_image(self, name):
        """Get image."""
        return self._get_image(name).attrs

    @atomic.action_timer("docker.tag_image")
    def tag_image(self, name, tags=None):
        """Add tag(s) to the image.

        :param name: name of the image
        :param tags: list of tags to add. If None, the random tag will be added
        """
        if tags is None:
            tags = [self.generate_random_name()]
        image = self._get_image(name)

        # TODO(andreykurilin): validate format of the tags before trying to
        #   adding them.
        for tag in tags:
            image.tag(name.split(":", 1)[0], tag)

        return self.get_image(name)

    @atomic.action_timer("docker.list_images")
    def list_images(self, all=False):
        """List all available images.

        :param all: Show intermediate image layers. By default, these are
            filtered out
        """
        return [i.attrs for i in self._client.images.list(all=all)]

    @atomic.action_timer("docker.run")
    def run_container(self, image_name, container_name=None, command=None,
                      detach=False, stdout=True, stderr=False, remove=True):
        """Run a container

        :param image_name: The name of image to launch
        :param container_name: The name of a container
        :param command: The command to run in the container.
        :param detach: Run container in the background.
            Defaults to False.
        :param stdout: Return logs from ``STDOUT`` when  ``detach=False``.
            Defaults to True.
        :param stderr: Return logs from ``STDERR`` when ``detach=False``.
            Defaults to False.
        :param remove: Remove the container when it has finished running.
            Defaults to True.
        """
        container_name = container_name or self.generate_random_name()
        return self._client.containers.run(
            image=self._fix_the_name(image_name), name=container_name,
            command=command,
            detach=detach, stdout=stdout, stderr=stderr, remove=remove)

    @atomic.action_timer("docker.create_network")
    def create_network(self, name=None, driver=None, options=None, ipam=None,
                       check_duplicate=None, internal=False, labels=None,
                       enable_ipv6=False, attachable=None, scope=None,
                       ingress=None):
        """Create a network

        :param name: Name of the network
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
        from docker import types

        name = name or self.generate_random_name()
        if ipam and not isinstance(ipam, types.IPAMConfig):
            pool_configs = [
                types.IPAMPool(**cfg) for cfg in ipam.get("Config", [])]
            ipam = types.IPAMConfig(ipam["Driver"],
                                    pool_configs=pool_configs,
                                    options=ipam["Options"])
        net = self._client.networks.create(
            name=name,
            driver=driver,
            options=options,
            ipam=ipam,
            check_duplicate=check_duplicate,
            internal=internal,
            labels=labels,
            enable_ipv6=enable_ipv6,
            attachable=attachable,
            scope=scope,
            ingress=ingress
        )
        return net.attrs

    @atomic.action_timer("docker.get_network")
    def get_network(self, network_id, verbose=False, scope=None):
        """Get network by ID.

        :param network_id: a Network ID
        :param verbose: Retrieve the service details across the cluster in
            swarm mode.
        :param scope: Filter the network by scope (``swarm``, ``global``
            or ``local``).
        """
        return self._client.networks.get(network_id=network_id,
                                         verbose=verbose,
                                         scope=scope).attrs

    @atomic.action_timer("docker.delete_network")
    def delete_network(self, network_id):
        """Remove a network by its ID"""
        self._client.networks.client.api.remove_network(network_id)

    @atomic.action_timer("docker.list_networks")
    def list_networks(self, ids=None, names=None, driver=None, label=None,
                      ntype=None, detailed=False):
        """List available networks.

        :param ids: List of ids to filter by.
        :param names: List of names to filter by.
        :param driver: a network driver to match
        :param label: label to match
        :param ntype: Filters networks by type.
        :param detailed: Grep detailed information about networks (aka greedy)
        """
        filters = {}
        if driver:
            filters["driver"] = driver
        if label:
            filters["label"] = label
        if ntype:
            filters["type"] = ntype
        return [n.attrs for n in self._client.networks.list(
            ids=ids or [],
            names=names or [],
            greedy=detailed, filters=filters)]
