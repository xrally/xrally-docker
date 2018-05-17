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

import sys

from rally.common.plugin import discover
from rally.common import validation

from xrally_docker.common.cleanup import manager
from xrally_docker.common.cleanup import resources
from xrally_docker.task import context
from xrally_docker.task import scenario


@validation.configure("check_cleanup_resources", platform="docker")
class CheckCleanupResourcesValidator(validation.Validator):

    def __init__(self):
        """Validates that docker resource managers exist."""
        super(CheckCleanupResourcesValidator, self).__init__()

    def validate(self, context, config, plugin_cls, plugin_cfg):
        res_mgrs = discover.itersubclasses(resources.ResourceManager)
        names = set([r._name for r in res_mgrs])

        missing = set(plugin_cfg)
        missing -= names
        missing = ", ".join(missing)
        if missing:
            return self.fail(
                "Couldn't find cleanup resource managers: %s" % missing)


@validation.add(name="check_cleanup_resources@docker")
# NOTE(amaretskiy): Set maximum order to run this last
@context.configure(name="cleanup", order=sys.maxsize, hidden=True)
class Cleanup(context.BaseDockerContext):
    """Context class for user resources cleanup."""

    CONFIG_SCHEMA = {
        "type": "array",
        "items": {
            "type": "string",
        }
    }

    def setup(self):
        # nothing to do here
        pass

    def cleanup(self):
        manager.cleanup(
            spec=self.context["env"]["platforms"]["docker"],
            superclass=scenario.BaseDockerScenario,
            owner_id=self.get_owner_id()
        )
