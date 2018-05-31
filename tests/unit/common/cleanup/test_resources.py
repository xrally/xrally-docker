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

import mock

from tests.unit import test
from xrally_docker.common.cleanup import resources


@resources.configure("foo")
class FakeResource(resources.ResourceManager):
    pass


@resources.configure("by")
class AnotherFakeResource(resources.ResourceManager):
    pass


class ResourceManagerTestCase(test.TestCase):
    def test_list(self):
        foo_objs = [mock.MagicMock(), mock.MagicMock()]
        client = mock.MagicMock()
        client.list_foos.return_value = foo_objs

        self.assertEqual(
            foo_objs,
            [r.raw_resource for r in FakeResource.list(client)])

    def test_attributes(self):
        res = {"Id": "iidd", "Name": "foo"}
        self.assertEqual("foo", FakeResource(res, None).name())
        self.assertEqual("iidd", FakeResource(res, None).id())

    def test_is_deleted(self):
        client = mock.MagicMock()

        client.get_foo.return_value = "foo"
        self.assertFalse(FakeResource(mock.MagicMock(), client).is_deleted())

        client.get_foo.side_effect = Exception()
        self.assertFalse(FakeResource(mock.MagicMock(), client).is_deleted())

        class NotFound(Exception):
            status_code = 404

        client.get_foo.side_effect = NotFound()
        self.assertTrue(FakeResource(mock.MagicMock(), client).is_deleted())

    def test_delete(self):
        raw_res = {"Id": "foo"}
        client = mock.MagicMock()

        FakeResource(raw_res, client).delete()
        client.delete_foo.assert_called_once_with("foo")


class ImageTestCase(object):
    def test_name(self):
        res = {"RepoTags": ["foo:bar", "xxx:yyy"]}
        self.assertEqual(
            ["bar", "yyy"],
            resources.Image(res, None).name())
