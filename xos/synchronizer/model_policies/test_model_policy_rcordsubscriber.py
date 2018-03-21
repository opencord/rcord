# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
from mock import patch, MagicMock
import mock
from xosconfig import Config

import os, sys

cwd=os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
xos_dir=os.path.abspath(os.path.join(cwd, "../../../../../../orchestration/xos/xos"))
services_dir=os.path.join(xos_dir, "../../xos_services")
config_file = os.path.join(cwd, "test_config.yaml")

# NOTE this have to start for xos_services
RCORD_XPROTO = "../profiles/rcord/xos/synchronizer/models/rcord.xproto"
OLT_XPROTO = "olt-service/xos/synchronizer/models/volt.xproto"

Config.clear()
Config.init(config_file, 'synchronizer-config-schema.yaml')

# FIXME move the synchronizer framework into a library
sys.path.append(xos_dir)
from synchronizers.new_base.mock_modelaccessor_build import build_mock_modelaccessor

class MockSubscriber:

    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']
        self.is_new = True
        self.id = 1

    def subscribed_links(self):
        pass

class MockAll:
    @staticmethod
    def all():
        pass

class MockService:

    def __init__(self):
        self.subscribed_dependencies = MockAll


class MockModel:
    def __init__(self):
        self.model_name = "VOLTService"

class MockLeaf:
    def __init__(self):
        self.leaf_model = MockModel()

class MockLink:
    def __init__(self):
        self.provider_service = MockLeaf()

class TestModelPolicyRCORDSubscriber(unittest.TestCase):
    def setUp(self):
        global model_accessor

        self.original_sys_path = sys.path

        # Generate a fake model accessor (emulate the client library)
        build_mock_modelaccessor(xos_dir, services_dir, [RCORD_XPROTO, OLT_XPROTO])

        import synchronizers.new_base.modelaccessor
        from synchronizers.new_base.modelaccessor import model_accessor
        from model_policy_rcordsubscriber import RCORDSubscriberPolicy

        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v

        # model_accessor.reset_all_object_stores()

        # create base objects for testing
        self.policy = RCORDSubscriberPolicy()

    def tearDown(self):
        sys.path = self.original_sys_path

    @patch.object(MockSubscriber, 'subscribed_links', MockAll)
    @patch.object(MockAll, 'all', MagicMock(return_value=['foo']))
    def test_update_and_do_nothing(self):
        si = MockSubscriber(name="myTestSubscriber")
        si.is_new = False
        self.policy.handle_create(si)
        # NOTE assert that no models are created

    @patch.object(MockSubscriber, 'subscribed_links', MockAll)
    @patch.object(MockAll, 'all', MagicMock(return_value=[MockLink]))
    def test_create(self):
        si = MockSubscriber(name="myTestSubscriber")
        owner = MockService()

        si.owner = owner

        with patch.object(owner.subscribed_dependencies, 'all', MagicMock(return_value=[MockLink()])), \
             patch.object(VOLTServiceInstance, "save", autospec=True) as save_volt, \
             patch.object(ServiceInstanceLink, "save", autospec=True) as save_link:
            self.policy.handle_create(si)
            self.assertEqual(save_link.call_count, 1)
            self.assertEqual(save_volt.call_count, 1)


if __name__ == '__main__':
    unittest.main()
