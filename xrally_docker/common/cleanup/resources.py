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


from rally.common import cfg

CONF = cfg.CONF


def configure(name, order=0, max_attempts=3,
              timeout=CONF.docker.resource_deletion_timeout,
              interval=1, threads=CONF.docker.cleanup_threads):
    """Decorator that overrides resource specification.

    Just put it on top of your resource class and specify arguments that you
    need.

    :param name: Name of resource(i.e. image, container, etc)
    :param order: Used to adjust priority of cleanup for different resource
                  types
    :param max_attempts: Max amount of attempts to delete single resource
    :param timeout: Max duration of deletion in seconds
    :param interval: Resource status pooling interval
    :param threads: Amount of threads (workers) that are deleting resources
                    simultaneously
    """

    def inner(cls):
        # TODO(boris-42): This can be written better I believe =)
        cls._name = name
        cls._order = order
        cls._timeout = timeout
        cls._max_attempts = max_attempts
        cls._interval = interval
        cls._threads = threads

        return cls

    return inner


class ResourceManager(object):
    """Base class for cleanup plugins for specific resources.

    You should use @resource decorator to specify major configuration of
    resource manager. Usually you should specify: name of resource and order.
    """

    @classmethod
    def list(cls, client):
        if cls._name.endswith("y"):
            name = cls._name[:-1] + "ies"
        else:
            name = cls._name + "s"
        list_method = getattr(client, "list_%s" % name)
        return [cls(obj, client) for obj in list_method()]

    def __init__(self, resource, client):
        self.raw_resource = resource
        self.client = client

    def id(self):
        """Returns id of resource."""
        return self.raw_resource["Id"]

    def name(self):
        """Returns name or a list of names for resource."""
        return self.raw_resource["Name"]

    def is_deleted(self):
        """Checks if the resource is deleted.

        Fetch resource by id from service and check it status.
        In case of NotFound or status is DELETED or DELETE_COMPLETE returns
        True, otherwise False.
        """
        try:
            get_method = getattr(self.client, "get_%s" % self._name)
            get_method(self.id())
        except Exception as e:
            return getattr(e, "code", getattr(e, "status_code", 400)) == 404

        return False

    def delete(self):
        """Delete resource that corresponds to instance of this class."""
        delete_method = getattr(self.client, "delete_%s" % self._name)
        delete_method(self.id())


@configure("image")
class Image(ResourceManager):
    def name(self):
        return [tag.split(":", 1)[1]
                for tag in self.raw_resource["RepoTags"]]


@configure("network")
class Network(ResourceManager):
    pass
