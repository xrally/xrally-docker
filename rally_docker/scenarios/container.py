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
import six

from rally_docker.scenarios import base


@base.configure("Docker.run_container", context={"images": {"existing": True}})
class RunContainer(base.BaseDockerScenario):
    @staticmethod
    def _parse_image_name(name):
        if ":" not in name:
            name = "%s:latest" % name
        return name

    @atomic.action_timer("pull_image")
    def _pull_image(self, image_name):
        return self.client().images.pull(image_name)

    @atomic.action_timer("run_container")
    def _run(self, image_name, container_name, command):
        output = self.client().containers.run(image=image_name,
                                              name=container_name,
                                              command=command)

        output = six.text_type(output).split("\n")
        self.add_output(complete={"title": "Script Output",
                                  "chart_plugin": "TextArea",
                                  "data": output})

    def run(self, image_name, command):
        image_name = self._parse_image_name(image_name)
        if image_name not in self.context["docker"]["images"]:
            self._pull_image(image_name)

        name = self.generate_random_name()
        self._run(image_name=image_name, container_name=name,
                  command=command)
