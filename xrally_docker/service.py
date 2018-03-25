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

from rally.task import atomic
from rally.task import service


class Docker(service.Service):
    def __init__(self, credentials, name_generator=None, atomic_inst=None):
        super(Docker, self).__init__(None, name_generator=name_generator,
                                     atomic_inst=atomic_inst)
        self._credentials = credentials
        import docker

        # TODO(andreykurilin): use credentials
        self._client = docker.DockerClient.from_env()

    @atomic.action_timer("docker.get_version")
    def get_version(self):
        """Get Docker version."""
        return self._client.version()["Version"]

    @staticmethod
    def _fix_the_name(name):
        """Add 'latest' tag if no tag in the name."""
        if ":" not in name:
            return "%s:latest" % name
        return name

    @atomic.action_timer("docker.pull")
    def pull_image(self, name):
        """Pull the image by name.

        It there is no tag in the name, only the latest tag will be used.
        """
        return self._client.images.pull(self._fix_the_name(name)).attrs

    @atomic.action_timer("docker.images")
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
