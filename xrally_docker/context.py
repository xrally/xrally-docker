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

from rally.task import context

from xrally_docker import service


def configure(name, order, hidden=False):
    return context.configure(name, platform="docker", order=order,
                             hidden=hidden)


class BaseDockerContext(context.Context):
    CONFIG_SCHEMA = {"type": "object", "additionalProperties": False}

    def __init__(self, ctx):
        super(BaseDockerContext, self).__init__(ctx)
        self.context.setdefault("docker", {})
        self.client = service.Docker(
            self.context["env"]["platforms"]["docker"],
            atomic_inst=self.atomic_actions(),
            name_generator=self.generate_random_name
        )
