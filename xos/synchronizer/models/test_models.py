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
from mock import patch, Mock, MagicMock

# mocking XOS exception, as they're based in Django
class Exceptions:
    XOSValidationError = Exception
    XOSProgrammingError = Exception
    XOSPermissionDenied = Exception

class XOS:
    exceptions = Exceptions

class TestRCORDModels(unittest.TestCase):
    def setUp(self):
        self.xos = XOS

        self.models_decl = Mock()
        self.models_decl.RCORDSubscriber_decl = MagicMock
        self.models_decl.RCORDSubscriber_decl.save = Mock()
        self.models_decl.RCORDSubscriber_decl.objects = Mock()
        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = []


        modules = {
            'xos.exceptions': self.xos.exceptions,
            'models_decl': self.models_decl
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

        self.volt = Mock()

        from models import RCORDSubscriber

        self.rcord_subscriber_class = RCORDSubscriber

        self.rcord_subscriber = RCORDSubscriber()
        self.rcord_subscriber.onu_device = "BRCM1234"
        self.rcord_subscriber.c_tag = "111"
        self.rcord_subscriber.ip_address = "1.1.1.1"
        self.rcord_subscriber.mac_address = "00:AA:00:00:00:01"
        self.rcord_subscriber.owner.leaf_model.access = "voltha"
        self.rcord_subscriber.owner.provider_services = [self.volt]


    def test_save(self):
        self.rcord_subscriber.save()
        self.models_decl.RCORDSubscriber_decl.save.assert_called()

    def test_validate_ip_address(self):
        self.rcord_subscriber.ip_address = "invalid"
        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()

        self.assertEqual(e.exception.message, "The ip_address you specified (invalid) is not valid")
        self.models_decl.RCORDSubscriber_decl.save.assert_not_called()

    def test_validate_mac_address(self):
        self.rcord_subscriber.mac_address = "invalid"
        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()

        self.assertEqual(e.exception.message, "The mac_address you specified (invalid) is not valid")
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

    def test_validate_c_tag(self):
        """
        check that other subscriber attached to the same ONU don't have the same c_tag
        """

        s = Mock()
        s.c_tag = "111"
        s.onu_device = "BRCM1234"

        self.models_decl.RCORDSubscriber_decl.objects.filter.return_value = [s]

        with self.assertRaises(Exception) as e:
            self.rcord_subscriber.save()

        self.assertEqual(e.exception.message, "The c_tag you specified (111) has already been used on device BRCM1234")
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


if __name__ == '__main__':
    unittest.main()
