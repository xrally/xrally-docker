# Copyright 2014: Mirantis Inc.
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

import time

from rally.common import broker
from rally.common import logging
from rally.common.plugin import discover
from rally.common.plugin import plugin
from rally.common import utils as rutils

from xrally_docker.common.cleanup import resources
from xrally_docker import service


LOG = logging.getLogger(__name__)


class SeekAndDestroy(object):

    def __init__(self, manager_cls, client, resource_classes=None,
                 owner_id=None):
        """Resource deletion class.

        This class contains method exterminate() that finds and deletes
        all resources created by Rally.

        :param manager_cls: subclass of base.ResourceManager
        :param client: a docker client instance
        :param resource_classes: Resource classes to match resource names
                                 against
        :param owner_id: The UUID of an owner to match resource names against
        """
        self.manager_cls = manager_cls
        self.client = client
        self.resource_classes = resource_classes or [
            rutils.RandomNameGeneratorMixin]
        self.owner_id = owner_id

    def _delete_single_resource(self, resource):
        """Safe resource deletion with retries and timeouts.

        Send request to delete resource, in case of failures repeat it few
        times. After that pull status of resource until it's deleted.

        Writes in LOG warning with UUID of resource that wasn't deleted

        :param resource: instance of resource manager initiated with resource
                         that should be deleted.
        """

        msg_kw = {
            "uuid": resource.id(),
            "name": "; ".join(resource.name()),
            "resource": resource._name
        }

        LOG.debug(
            "Deleting docker.%(resource)s object %(name)s (%(uuid)s)"
            % msg_kw)

        try:
            rutils.retry(resource._max_attempts, resource.delete)
        except Exception as e:
            msg = ("Resource deletion failed, max retries exceeded for "
                   "docker.%(resource)s: %(uuid)s.") % msg_kw

            if logging.is_debug():
                LOG.exception(msg)
            else:
                LOG.warning("%(msg)s Reason: %(e)s" % {"msg": msg, "e": e})
        else:
            started = time.time()
            failures_count = 0
            while time.time() - started < resource._timeout:
                try:
                    if resource.is_deleted():
                        return
                except Exception as e:
                    LOG.exception(
                        "Seems like %s.%s.is_deleted(self) method is broken "
                        "It shouldn't raise any exceptions."
                        % (resource.__module__, type(resource).__name__))

                    # NOTE(boris-42): Avoid LOG spamming in case of bad
                    #                 is_deleted() method
                    failures_count += 1
                    if failures_count > resource._max_attempts:
                        break

                finally:
                    rutils.interruptable_sleep(resource._interval)

            LOG.warning("Resource deletion failed, timeout occurred for "
                        "docker.%(resource)s: %(uuid)s." % msg_kw)

    def _publisher(self, queue):
        """Publisher for deletion jobs.

        This method lists all resources (using manager_cls) and puts jobs for
        deletion.
        """

        try:
            for raw_resource in rutils.retry(
                    3, self.manager_cls.list, self.client):
                queue.append(raw_resource)
        except Exception:
            LOG.exception(
                "Seems like %s.%s.list(self) method is broken. "
                "It shouldn't raise any exceptions."
                % (self.manager_cls.__module__, self.manager_cls.__name__))

    def _consumer(self, cache, raw_resource):
        """Method that consumes single deletion job."""

        names = raw_resource.name()
        if not isinstance(names, list):
            names = [names]

        for name in names:
            if rutils.name_matches_object(
                    name, *self.resource_classes,
                    task_id=self.owner_id, exact=False):
                self._delete_single_resource(raw_resource)
                break

    def exterminate(self):
        """Delete all resources for passed resource_mgr."""

        broker.run(self._publisher, self._consumer,
                   consumers_count=self.manager_cls._threads)


def find_resource_managers(names=None):
    """Returns resource managers.

    :param names: List of names that is used for filtering resource manager
        classes
    """
    names = set(names or [])

    resource_managers = []
    for manager in discover.itersubclasses(resources.ResourceManager):
        if manager._name in names:
            resource_managers.append(manager)

    resource_managers.sort(key=lambda x: x._order)

    found_names = set()
    for mgr in resource_managers:
        found_names.add(mgr._name)

    missing = names - found_names
    if missing:
        LOG.warning("Missing resource managers: %s" % ", ".join(missing))

    return resource_managers


def cleanup(spec, names=None, superclass=plugin.Plugin, owner_id=None):
    """Generic cleaner.

    This method goes through all plugins. Filter those and left only plugins
    with _service from services or _resource from resources.

    :param spec: a spec for Docker client
    :param names: Use only resource managers that have names in this list.
    :param superclass: The plugin superclass to perform cleanup
                       for. E.g., this could be
                       ``rally.task.scenario.Scenario`` to cleanup all
                       Scenario resources.
    :param owner_id: The UUID of an owner of resource. If it was created at
        workload level, it should be workload UUID. If it was created at
        subtask level, it should be subtask UUID.
    """
    resource_classes = [cls for cls in discover.itersubclasses(superclass)
                        if issubclass(cls, rutils.RandomNameGeneratorMixin)]
    if not resource_classes and issubclass(superclass,
                                           rutils.RandomNameGeneratorMixin):
        resource_classes.append(superclass)

    docker = service.Docker(spec)

    for manager in find_resource_managers(names):
        LOG.debug("Cleaning up docker %s objects" % manager._name)
        SeekAndDestroy(manager, docker,
                       resource_classes=resource_classes,
                       owner_id=owner_id).exterminate()
