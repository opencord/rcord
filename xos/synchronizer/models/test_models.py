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
import os
import sys
from mock import patch, Mock, MagicMock

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
service_dir = os.path.join(test_path, "../../../..")
xos_dir = os.path.join(test_path, "../../..")
if not os.path.exists(os.path.join(test_path, "new_base")):
    xos_dir = os.path.join(test_path, "../../../../../../orchestration/xos/xos")
    services_dir = os.path.join(xos_dir, "../../xos_services")

# mocking XOS exception, as they're based in Django


class Exceptions:
    XOSValidationError = Exception
    XOSProgrammingError = Exception
    XOSPermissionDenied = Exception
    XOSConfigurationError = Exception


class XOS:
    exceptions = Exceptions


class TestRCORDModels(unittest.TestCase):
    def setUp(self):

        self.sys_path_save = sys.path
        sys.path.append(xos_dir)

        self.xos = XOS

        self.models_decl = Mock()
        self.models_decl.RCORDSubscriber_decl = MagicMock
        self.models_decl.RCORDSubscriber_decl.save = Mock()
        self.models_decl.RCORDSubscriber_decl.objects = Mock()
        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = []

        self.models_decl.RCORDIpAddress_decl = MagicMock
        self.models_decl.RCORDIpAddress_decl.save = Mock()
        self.models_decl.RCORDIpAddress_decl.objects = Mock()
        self.models_decl.RCORDIpAddress_decl.objects.filter.return_value = []

        modules = {
            'xos.exceptions': self.xos.exceptions,
            'models_decl': self.models_decl
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

        from models import RCORDSubscriber, RCORDIpAddress

        self.volt = Mock(name="vOLT")
        self.volt.leaf_model.name = "vOLT"
        self.volt.get_olt_technology_from_unu_sn.return_value = "xgspon"


        self.rcord_subscriber_class = RCORDSubscriber

        self.rcord_subscriber = RCORDSubscriber()
        self.rcord_subscriber.deleted = False
        self.rcord_subscriber.id = None  # this is a new model
        self.rcord_subscriber.is_new = True
        self.rcord_subscriber.onu_device = "BRCM1234"
        self.rcord_subscriber.c_tag = 111
        self.rcord_subscriber.s_tag = 222
        self.rcord_subscriber.ips = Mock()
        self.rcord_subscriber.ips.all.return_value = []
        self.rcord_subscriber.mac_address = "00:AA:00:00:00:01"
        self.rcord_subscriber.owner.leaf_model.access = "voltha"
        self.rcord_subscriber.owner.provider_services = [self.volt]
        self.rcord_subscriber.list_of_unused_c_tags_for_s_tag = []


        self.rcord_ip = RCORDIpAddress()
        self.rcord_ip.subscriber = 1

    # TODO add a test for validate_tech_profile_id

    def tearDown(self):
        sys.path = self.sys_path_save

    def test_save(self):
        self.rcord_subscriber.save()
        self.models_decl.RCORDSubscriber_decl.save.assert_called()

    def _test_validate_ipv4_address(self):
        self.rcord_ip.ip = "192.168.0."
        with self.assertRaises(Exception) as e:
            self.rcord_ip.save()

        self.assertEqual(e.exception.message, "The IP specified is not valid: 192.168.0.")
        self.models_decl.RCORDIpAddress.save.assert_not_called()

    def test_validate_ipv6_address(self):
        self.rcord_ip.ip = "2001:0db8:85a3:0000:0000:8a2e:03"
        with self.assertRaises(Exception) as e:
            self.rcord_ip.save()

        self.assertEqual(e.exception.message, "The IP specified is not valid: 2001:0db8:85a3:0000:0000:8a2e:03")
        self.models_decl.RCORDIpAddress.save.assert_not_called()

    def test_validate_mac_address(self):
        self.rcord_subscriber.mac_address = "invalid"
        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()

        self.assertEqual(e.exception.message, "The MAC address specified is not valid: invalid")
        self.models_decl.RCORDSubscriber_decl.save.assert_not_called()

    def test_valid_onu_device(self):
        self.rcord_subscriber.save()
        self.models_decl.RCORDSubscriber_decl.save.assert_called()

    def test_invalid_onu_device(self):
        self.volt.leaf_model.has_access_device.return_value = False
        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()

        self.assertEqual(e.exception.message, "The onu_device you specified (BRCM1234) does not exists")
        self.models_decl.RCORDSubscriber_decl.save.assert_not_called()

    def test_missing_onu_device_on_delete(self):
        self.volt.leaf_model.has_access_device.return_value = False
        self.rcord_subscriber.deleted = True
        self.rcord_subscriber.save()
        self.models_decl.RCORDSubscriber_decl.save.assert_called()

    def test_validate_c_tag_pass(self):
        """
        check that other subscriber attached to the same ONU don't have the same c_tag
        """

        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = [self.rcord_subscriber]

        self.rcord_subscriber.save()

        self.models_decl.RCORDSubscriber_decl.save.assert_called()

    def test_validate_c_tag_fail(self):
        """
        check that other subscriber attached to the same ONU don't have the same c_tag
        """

        s = Mock()
        s.c_tag = 111
        s.onu_device = "BRCM1234"

        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = [s, self.rcord_subscriber]

        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()

        self.assertEqual(e.exception.message, "The c_tag you specified (111) has already been used on device BRCM1234")
        self.models_decl.RCORDSubscriber_decl.save.assert_not_called()

    def test_validate_get_used_s_c_tag_subscriber_id(self):
        """
        check that other subscriber using the same s_tag don't have the same c_tag
        """
        s1 = Mock()
        s1.id = 456
        s1.c_tag = 999
        s1.s_tag = 222
        s1.onu_device = "BRCM1234"

        s2 = Mock()
        s2.id = 123
        s2.c_tag = 111
        s2.s_tag = 222
        s2.onu_device = "BRCM12345"

        self.rcord_subscriber.get_same_onu_subscribers = Mock()
        self.rcord_subscriber.get_same_onu_subscribers.return_value = [s1]

        self.rcord_subscriber.get_same_s_c_tag_subscribers = Mock()
        self.rcord_subscriber.get_same_s_c_tag_subscribers.return_value = [s2]

        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()

        self.assertEqual(e.exception.message,
                         "The c_tag(111) and s_tag(222) pair you specified,has already been used by Subscriber with Id (123)")
        self.models_decl.RCORDSubscriber_decl.save.assert_not_called()

    def test_validate_c_tag_on_update(self):
        s = Mock()
        s.c_tag = 111
        s.onu_device = "BRCM1234"
        s.id = 1

        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = [s]

        self.rcord_subscriber.is_new = False
        self.rcord_subscriber.id = 1
        self.rcord_subscriber.save()

        self.models_decl.RCORDSubscriber_decl.save.assert_called()

    def test_validate_c_tag_on_update_fail(self):
        s = Mock()
        s.c_tag = 222
        s.onu_device = "BRCM1234"
        s.id = 2

        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = [s]

        self.rcord_subscriber.id = 1
        self.rcord_subscriber.is_new = False
        self.rcord_subscriber.c_tag = 222
        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()

        self.assertEqual(e.exception.message, "The c_tag you specified (222) has already been used on device BRCM1234")
        self.models_decl.RCORDSubscriber_decl.save.assert_not_called()

    def test_generate_c_tag(self):
        s = Mock()
        s.c_tag = "111"
        s.s_tag = "223"
        s.onu_device = "BRCM1234"
        
        self.rcord_subscriber.get_same_onu_subscribers = Mock()
        self.rcord_subscriber.get_same_onu_subscribers.return_value = [s]

        self.rcord_subscriber.get_same_s_c_tag_subscribers = Mock()
        self.rcord_subscriber.get_same_s_c_tag_subscribers.return_value = []

        self.rcord_subscriber.c_tag = None

        self.rcord_subscriber.save()

        self.models_decl.RCORDSubscriber_decl.save.assert_called()
        self.assertNotEquals(self.rcord_subscriber.c_tag, "111")
        self.assertGreater(self.rcord_subscriber.c_tag, 16)
        self.assertLess(self.rcord_subscriber.c_tag, 4097)

        #Testing whether the random generation choses c_tag from the list provided
        self.rcord_subscriber.c_tag = None
        self.rcord_subscriber.s_tag = None
        self.rcord_subscriber.unused_c_tags_for_s_tag = Mock()
        self.rcord_subscriber.unused_c_tags_for_s_tag.return_value = [18,19]

        self.rcord_subscriber.save()
        self.models_decl.RCORDSubscriber_decl.save.assert_called()
        self.assertGreater(self.rcord_subscriber.c_tag, 17)
        self.assertLess(self.rcord_subscriber.c_tag, 20)

        self.rcord_subscriber.c_tag = None
        self.rcord_subscriber.s_tag = None

        self.rcord_subscriber.save()
        self.models_decl.RCORDSubscriber_decl.save.assert_called()
        self.assertGreater(self.rcord_subscriber.c_tag, 16)
        self.assertLess(self.rcord_subscriber.c_tag, 4096)

    def test_unused_c_tags_for_s_tag(self):
        s=[]
        for i in range(16,4097):
            d = Mock()
            d.c_tag = i
            d.s_tag = "222"
            d.onu_device = "BRCM1234"
            s.append(d)

        self.rcord_subscriber.get_same_onu_subscribers = Mock()
        self.rcord_subscriber.get_same_onu_subscribers.return_value = []
        self.rcord_subscriber.get_same_s_c_tag_subscribers = Mock()
        self.rcord_subscriber.get_same_s_c_tag_subscribers.return_value = []

        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = s
        self.rcord_subscriber.s_tag = 222
        self.rcord_subscriber.c_tag = None
        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()
        self.assertEqual(e.exception.message, "All the c_tags are exhausted for this s_tag: 222")
        self.models_decl.RCORDSubscriber_decl.save.assert_not_called()

    def test_unused_s_tags_for_c_tag(self):
        s=[]
        for i in range(16,4097):
            d = Mock()
            d.s_tag = i
            d.c_tag = "111"
            d.onu_device = "BRCM1234"
            s.append(d)

        self.rcord_subscriber.get_same_onu_subscribers = Mock()
        self.rcord_subscriber.get_same_onu_subscribers.return_value = []
        self.rcord_subscriber.get_same_s_c_tag_subscribers = Mock()
        self.rcord_subscriber.get_same_s_c_tag_subscribers.return_value = []

        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = s
        self.rcord_subscriber.c_tag = 111
        self.rcord_subscriber.s_tag = None
        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()
        self.assertEqual(e.exception.message, "All the s_tags are exhausted for this c_tag: 111")
        self.models_decl.RCORDSubscriber_decl.save.assert_not_called()



    def test_generate_s_tag(self):
        self.rcord_subscriber.s_tag = None

        self.rcord_subscriber.save()

        self.models_decl.RCORDSubscriber_decl.save.assert_called()
        self.assertNotEqual(self.rcord_subscriber.s_tag, None)


    def test_provisioned_s_stag(self):
        self.rcord_subscriber.save()
        self.models_decl.RCORDSubscriber_decl.save.assert_called()
        self.assertEqual(self.rcord_subscriber.s_tag, 222)


if __name__ == '__main__':
    unittest.main()
