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
from rally.common import utils

from tests.unit import test
from xrally_docker.common.cleanup import manager


BASE = "xrally_docker.common.cleanup.manager"


class SeekAndDestroyTestCase(test.TestCase):

    @mock.patch("%s.LOG" % BASE)
    def test__delete_single_resource(self, mock_log):
        mock_resource = mock.MagicMock(_max_attempts=3, _timeout=10,
                                       _interval=0.01)
        mock_resource.delete.side_effect = [Exception, Exception, True]
        mock_resource.is_deleted.side_effect = [False, False, True]

        manager.SeekAndDestroy(None, None)._delete_single_resource(
            mock_resource)

        mock_resource.delete.assert_has_calls([mock.call()] * 3)
        self.assertEqual(3, mock_resource.delete.call_count)
        mock_resource.is_deleted.assert_has_calls([mock.call()] * 3)
        self.assertEqual(3, mock_resource.is_deleted.call_count)

        # NOTE(boris-42): No logs and no exceptions means no bugs!
        self.assertEqual(0, mock_log.call_count)

    @mock.patch("%s.LOG" % BASE)
    def test__delete_single_resource_timeout(self, mock_log):

        mock_resource = mock.MagicMock(_max_attempts=1, _timeout=0.02,
                                       _interval=0.025)

        mock_resource.delete.return_value = True
        mock_resource.is_deleted.side_effect = [False, False, True]

        manager.SeekAndDestroy(None, None)._delete_single_resource(
            mock_resource)

        mock_resource.delete.assert_called_once_with()
        mock_resource.is_deleted.assert_called_once_with()

        self.assertEqual(1, mock_log.warning.call_count)

    @mock.patch("%s.LOG" % BASE)
    def test__delete_single_resource_exception_in_is_deleted(self, mock_log):
        mock_resource = mock.MagicMock(_max_attempts=3, _timeout=10,
                                       _interval=0)
        mock_resource.delete.return_value = True
        mock_resource.is_deleted.side_effect = [Exception] * 4
        manager.SeekAndDestroy(None, None)._delete_single_resource(
            mock_resource)

        mock_resource.delete.assert_called_once_with()
        self.assertEqual(4, mock_resource.is_deleted.call_count)

        self.assertEqual(1, mock_log.warning.call_count)
        self.assertEqual(4, mock_log.exception.call_count)

    def test__publisher(self):
        mock_mgr = mock.MagicMock()
        mock_mgr.list.side_effect = [Exception, Exception, [1, 2, 3]]
        client = mock.MagicMock()
        publish = manager.SeekAndDestroy(mock_mgr, client)._publisher

        queue = []
        publish(queue)

        self.assertEqual([mock.call(client)] * 3,
                         mock_mgr.list.call_args_list)
        self.assertEqual(queue, [1, 2, 3])

    @mock.patch("rally.common.utils.name_matches_object")
    @mock.patch("%s.SeekAndDestroy._delete_single_resource" % BASE)
    def test__consumer(self, mock__delete_single_resource,
                       mock_name_matches_object):

        client = mock.MagicMock()

        mock_mgr = mock.MagicMock()
        mock_mgr.name.return_value = ["xxx", "yyy", "s_rally"]
        resource_classes = [mock.Mock()]
        owner_id = "task_id"
        mock_name_matches_object.return_value = True

        consumer = manager.SeekAndDestroy(
            mock_mgr, client, resource_classes=resource_classes,
            owner_id=owner_id)._consumer

        consumer(None, mock_mgr)

        mock__delete_single_resource.assert_called_once_with(
            mock_mgr)

    @mock.patch("%s.broker.run" % BASE)
    def test_exterminate(self, mock_broker_run):
        manager_cls = mock.MagicMock(_threads=5)
        cleaner = manager.SeekAndDestroy(manager_cls, None)
        cleaner._publisher = mock.Mock()
        cleaner._consumer = mock.Mock()
        cleaner.exterminate()

        mock_broker_run.assert_called_once_with(cleaner._publisher,
                                                cleaner._consumer,
                                                consumers_count=5)


class ManagerHelpersTestCase(test.TestCase):

    def _get_res_mock(self, **kw):
        _mock = mock.MagicMock()
        for k, v in kw.items():
            setattr(_mock, k, v)
        return _mock

    @mock.patch("%s.discover.itersubclasses" % BASE)
    def test_find_resource_managers(self, mock_itersubclasses):
        mock_itersubclasses.return_value = [
            self._get_res_mock(_name="fake", _order=1),
            self._get_res_mock(_name="other", _order=2)
        ]

        self.assertEqual([mock_itersubclasses.return_value[0]],
                         manager.find_resource_managers(names=["fake"]))

        self.assertEqual(
            [mock_itersubclasses.return_value[0],
             mock_itersubclasses.return_value[1]],
            manager.find_resource_managers(names=["fake", "other"]))

    @mock.patch("%s.service.Docker" % BASE)
    @mock.patch("rally.common.plugin.discover.itersubclasses")
    @mock.patch("%s.SeekAndDestroy" % BASE)
    @mock.patch("%s.find_resource_managers" % BASE,
                return_value=[mock.MagicMock(), mock.MagicMock()])
    def test_cleanup(self, mock_find_resource_managers, mock_seek_and_destroy,
                     mock_itersubclasses, mock_docker):
        class A(utils.RandomNameGeneratorMixin):
            pass

        class B(object):
            pass

        mock_itersubclasses.return_value = [A, B]

        manager.cleanup(names=["a", "b"], spec={},
                        superclass=A,
                        owner_id="task_id")

        mock_find_resource_managers.assert_called_once_with(["a", "b"])

        mock_seek_and_destroy.assert_has_calls([
            mock.call(mock_find_resource_managers.return_value[0],
                      mock_docker.return_value,
                      resource_classes=[A], owner_id="task_id"),
            mock.call().exterminate(),
            mock.call(mock_find_resource_managers.return_value[1],
                      mock_docker.return_value,
                      resource_classes=[A], owner_id="task_id"),
            mock.call().exterminate()
        ])
