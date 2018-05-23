
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
import re
import socket
import random

from xos.exceptions import XOSValidationError, XOSProgrammingError, XOSPermissionDenied
from models_decl import RCORDService_decl, RCORDSubscriber_decl

class RCORDService(RCORDService_decl):
    class Meta:
        proxy = True

class RCORDSubscriber(RCORDSubscriber_decl):

    class Meta:
        proxy = True

    def invalidate_related_objects(self):
        # Dirty all vSGs related to this subscriber, so the vSG synchronizer
        # will run.

        # FIXME: This should be reimplemented when multiple-objects-per-synchronizer is implemented.

        for link in self.subscribed_links.all():
            outer_service_instance = link.provider_service_instance
            # TODO: We may need to invalide the vOLT too...
            for link in outer_service_instance.subscribed_links.all():
                inner_service_instance = link.provider_service_instance
                inner_service_instance.save(update_fields=["updated"])

    def generate_tag(self):
        # NOTE this method will loop if available c_tags are ended
        tag = random.randint(16, 4096)
        if tag in self.get_used_c_tags():
            return self.generate_tag()
        return tag

    def get_used_c_tags(self):
        same_onu_subscribers = RCORDSubscriber.objects.filter(onu_device=self.onu_device)
        return [s.c_tag for s in same_onu_subscribers]

    def save(self, *args, **kwargs):

        self.validate_unique_service_specific_id(none_okay=True)

        # VSGServiceInstance will extract the creator from the Subscriber, as it needs a creator to create its
        # Instance.
        if not self.creator:
            # If we weren't passed an explicit creator, then we will assume the caller is the creator.
            if not getattr(self, "caller", None):
                raise XOSProgrammingError("RCORDSubscriber's self.caller was not set")
            self.creator = self.caller

        if (not hasattr(self, 'caller') or not self.caller.is_admin):
            if (self.has_field_changed("service_specific_id")):
                raise XOSPermissionDenied("You do not have permission to change service_specific_id")

        # validate IP Address
        if hasattr(self, 'ip_address') and self.ip_address is not None:
            try:
                socket.inet_aton(self.ip_address)
            except socket.error:
                raise XOSValidationError("The ip_address you specified (%s) is not valid" % self.ip_address)

        # validate MAC Address
        if hasattr(self, 'mac_address') and self.mac_address is not None:
            if not re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", self.mac_address.lower()):
                raise XOSValidationError("The mac_address you specified (%s) is not valid" % self.mac_address)

        # validate c_tag
        if hasattr(self, 'c_tag') and self.c_tag is not None:
            is_update_with_same_tag = False

            if not self.is_new:
                # if it is an update, but the tag is the same, skip validation
                existing = RCORDSubscriber.objects.filter(c_tag=self.c_tag)

                if len(existing) > 0 and existing[0].c_tag == self.c_tag and existing[0].id == self.id:
                    is_update_with_same_tag = True

            if self.c_tag in self.get_used_c_tags() and not is_update_with_same_tag:
                raise XOSValidationError("The c_tag you specified (%s) has already been used on device %s" % (self.c_tag, self.onu_device))

        if not hasattr(self, "c_tag") or self.c_tag is None:
            self.c_tag = self.generate_tag()

        self.set_owner()

        if hasattr(self.owner.leaf_model, "access") and self.owner.leaf_model.access == "voltha":

            # if the access network is managed by voltha, validate that onu_device actually exist
            volt_service = self.owner.provider_services[0].leaf_model # we assume RCORDService is connected only to the vOLTService

            if not volt_service.has_access_device(self.onu_device):
                raise XOSValidationError("The onu_device you specified (%s) does not exists" % self.onu_device)

        super(RCORDSubscriber, self).save(*args, **kwargs)
        self.invalidate_related_objects()
        return