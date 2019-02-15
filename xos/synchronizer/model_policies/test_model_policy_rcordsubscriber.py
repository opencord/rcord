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
from mock import patch, Mock


import os, sys

test_path=os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

class TestModelPolicyRCORDSubscriber(unittest.TestCase):
    def setUp(self):

        self.sys_path_save = sys.path

        config = os.path.join(test_path, "../test_config.yaml")
        from xosconfig import Config
        Config.clear()
        Config.init(config, 'synchronizer-config-schema.yaml')

        from xossynchronizer.mock_modelaccessor_build import mock_modelaccessor_config
        mock_modelaccessor_config(test_path, [
            ("rcord", "rcord.xproto"),
            ("olt-service", "volt.xproto")])

        import xossynchronizer.modelaccessor
        import mock_modelaccessor
        reload(mock_modelaccessor) # in case nose2 loaded it in a previous test
        reload(xossynchronizer.modelaccessor)      # in case nose2 loaded it in a previous test

        from xossynchronizer.modelaccessor import model_accessor
        self.model_accessor = model_accessor

        from model_policy_rcordsubscriber import RCORDSubscriberPolicy

        from mock_modelaccessor import MockObjectList

        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v

        # Some of the functions we call have side-effects. For example, creating a VSGServiceInstance may lead to creation of
        # tags. Ideally, this wouldn't happen, but it does. So make sure we reset the world.
        model_accessor.reset_all_object_stores()

        self.policy = RCORDSubscriberPolicy(model_accessor=self.model_accessor)
        self.si = Mock(name="myTestSubscriber")

    def tearDown(self):
        sys.path = self.sys_path_save

    def test_update_pre_provisione(self):
        si = self.si
        si.status = "pre-provisioned"
        self.policy.handle_create(si)

        with patch.object(VOLTServiceInstance, "save", autospec=True) as save_volt, \
             patch.object(ServiceInstanceLink, "save", autospec=True) as save_link:

            self.policy.handle_create(si)
            self.assertEqual(save_link.call_count, 0)
            self.assertEqual(save_volt.call_count, 0)

    def test_update_and_do_nothing(self):
        si = self.si
        si.is_new = False
        si.subscribed_links.all.return_value = ["already", "have", "a", "chain"]
        
        with patch.object(VOLTServiceInstance, "save", autospec=True) as save_volt, \
             patch.object(ServiceInstanceLink, "save", autospec=True) as save_link:

            self.policy.handle_create(si)
            self.assertEqual(save_link.call_count, 0)
            self.assertEqual(save_volt.call_count, 0)

    def test_create_chain(self):
        volt = Mock()
        volt.get_service_instance_class_name.return_value = "VOLTServiceInstance"

        service_dependency = Mock()
        service_dependency.provider_service = volt

        si = self.si
        si.is_new = True
        si.status = "enabled"
        si.subscribed_links.all.return_value = []
        si.owner.subscribed_dependencies.all.return_value = [service_dependency]

        with patch.object(VOLTServiceInstance, "save", autospec=True) as save_volt, \
             patch.object(ServiceInstanceLink, "save", autospec=True) as save_link:

            self.policy.handle_create(si)
            self.assertEqual(save_link.call_count, 1)
            self.assertEqual(save_volt.call_count, 1)

    def test_remove_chain(self):
        volt = VOLTServiceInstance()
        volt.name = "volt"

        link = ServiceInstanceLink()
        link.subscriber_service_instance= self.si
        link.provider_service_instance = volt
        link.provider_service_instance.leaf_model = volt


        si = self.si
        si.is_new = False
        si.status = "awaiting-auth"
        si.subscribed_links.all.return_value = [link]

        with patch.object(VOLTServiceInstance, "delete", autospec=True) as delete_volt, \
             patch.object(ServiceInstanceLink, "delete", autospec=True) as delete_link:

            self.policy.handle_create(si)
            self.assertEqual(delete_link.call_count, 1)
            self.assertEqual(delete_volt.call_count, 1)


if __name__ == '__main__':
    unittest.main()
