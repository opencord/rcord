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
import os, sys
from mock import patch, Mock, MagicMock

test_path=os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
service_dir=os.path.join(test_path, "../../../..")
xos_dir=os.path.join(test_path, "../../..")
if not os.path.exists(os.path.join(test_path, "new_base")):
    xos_dir=os.path.join(test_path, "../../../../../../orchestration/xos/xos")
    services_dir=os.path.join(xos_dir, "../../xos_services")

# mocking XOS exception, as they're based in Django
class Exceptions:
    XOSValidationError = Exception
    XOSProgrammingError = Exception
    XOSPermissionDenied = Exception

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

        self.volt = Mock()

        from models import RCORDSubscriber, RCORDIpAddress

        self.rcord_subscriber_class = RCORDSubscriber

        self.rcord_subscriber = RCORDSubscriber()
        self.rcord_subscriber.deleted = False
        self.rcord_subscriber.id = None # this is a new model
        self.rcord_subscriber.is_new = True
        self.rcord_subscriber.onu_device = "BRCM1234"
        self.rcord_subscriber.c_tag = 111
        self.rcord_subscriber.s_tag = 222
        self.rcord_subscriber.ips = Mock()
        self.rcord_subscriber.ips.all.return_value = []
        self.rcord_subscriber.mac_address = "00:AA:00:00:00:01"
        self.rcord_subscriber.owner.leaf_model.access = "voltha"
        self.rcord_subscriber.owner.provider_services = [self.volt]

        self.rcord_ip = RCORDIpAddress()
        self.rcord_ip.subscriber = 1;

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

    def _test_validate_c_tag_on_same_s_tag(self):
        """
        check that other subscriber using the same s_tag don't have the same c_tag
        """
        s = Mock()
        s.id = 123
        s.c_tag = 111
        s.s_tag = 222
        s.onu_device = "BRCM1234"

        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()

        self.assertEqual(e.exception.message, "The c_tag you specified (111) has already been used by Subscriber with id 123 and the same s_tag: 222")
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
        s.onu_device = "BRCM1234"

        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = [s]
        self.rcord_subscriber.c_tag = None

        self.rcord_subscriber.save()

        self.models_decl.RCORDSubscriber_decl.save.assert_called()
        self.assertNotEquals(self.rcord_subscriber.c_tag, "111")
        self.assertGreater(self.rcord_subscriber.c_tag, 16)
        self.assertLess(self.rcord_subscriber.c_tag, 4097)

    def test_generate_s_tag(self):
        self.rcord_subscriber.c_tag = None

        self.rcord_subscriber.save()

        self.models_decl.RCORDSubscriber_decl.save.assert_called()
        self.assertNotEqual(self.rcord_subscriber.s_tag, None)

    def test_provisioned_s_stag(self):
        self.rcord_subscriber.save()
        self.models_decl.RCORDSubscriber_decl.save.assert_called()
        self.assertEqual(self.rcord_subscriber.s_tag, 222)



if __name__ == '__main__':
    unittest.main()
