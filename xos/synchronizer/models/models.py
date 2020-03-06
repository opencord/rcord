
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
from django.core.exceptions import ObjectDoesNotExist
from xos.exceptions import XOSValidationError, XOSProgrammingError, XOSPermissionDenied, XOSConfigurationError
from models_decl import RCORDService_decl, RCORDSubscriber_decl, RCORDIpAddress_decl, BandwidthProfile_decl, RCORDUniTagInformation_decl

range_of_tags = list(range(16, 4095))

class RCORDUniTagInformation(RCORDUniTagInformation_decl):

    class Meta:
        proxy = True

    def validate_c_tag(self):
        if self.pon_c_tag not in range_of_tags:
            raise XOSValidationError("C-TAG out of range [16,4094]")
        # TODO: validate c_tag
        return True

    def validate_pair_c_s_tag(self):
        if self.pon_s_tag not in range_of_tags:
            raise XOSValidationError("S-TAG out of range [16,4094]")
        # TODO: validate s-c tag pair
        return True

    def validate_tech_profile_id(self):
        subs = RCORDSubscriber.object.filter(id=self.subscriber_id)

        if hasattr(subs.owner.leaf_model, "access") and \
                subs.owner.leaf_model.access != "voltha" and \
                not self.deleted:
            # if we're not using VOLTHA we don't need to validate this
            return True

        volt = None
        for ps in subs.owner.provider_services:
            provider_service = ps.leaf_model
            if provider_service.name.lower() == "volt":
                volt = provider_service

        # When interacting with VOLT-service remove the -X from onu_device
        technology = volt.get_olt_technology_from_unu_sn(subs.onu_device.split('-')[0])
        try:
            tp = volt.get_tech_profile(technology, self.tech_profile_id)
            return True
        except ObjectDoesNotExist:
            return False

    def save(self, *args, **kwargs):
        self.validate_unique_service_specific_id(none_okay=True)

        # Check VLAN TAGs
        self.validate_c_tag()
        self.validate_pair_c_s_tag()

        if not self.validate_tech_profile_id():
            raise XOSValidationError("The technology profile you specified [%s] does not exist" % self.tech_profile_id)

        super(RCORDUniTagInformation, self).save(*args, **kwargs)
        return


class BandwidthProfile(BandwidthProfile_decl):
    class Meta:
        proxy = True


class RCORDService(RCORDService_decl):
    class Meta:
        proxy = True


class RCORDIpAddress(RCORDIpAddress_decl):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        try:
            if ":" in self.ip:
                # it's an IPv6 address
                socket.inet_pton(socket.AF_INET6, self.ip)
            else:
                # it's an IPv4 address
                socket.inet_pton(socket.AF_INET, self.ip)
        except socket.error:
            raise XOSValidationError("The IP specified is not valid: %s" % self.ip)
        super(RCORDIpAddress, self).save(*args, **kwargs)
        return


class RCORDSubscriber(RCORDSubscriber_decl):

    class Meta:
        proxy = True

    def invalidate_related_objects(self):
        # Dirty all vSGs related to this subscriber, so the vSG synchronizer
        # will run.

        # FIXME: This should be reimplemented when multiple-objects-per-synchronizer is implemented.

        for link in self.subscribed_links.all():
            outer_service_instance = link.provider_service_instance
            # TODO: We may need to invalidate the vOLT too...
            for link in outer_service_instance.subscribed_links.all():
                inner_service_instance = link.provider_service_instance
                inner_service_instance.save(update_fields=["updated"])


    def save(self, *args, **kwargs):
        self.validate_unique_service_specific_id(none_okay=True)

        # VSGServiceInstance will extract the creator from the Subscriber,
        # as it needs a creator to create its Instance.
        if not self.creator:
            # If we weren't passed an explicit creator, then we will assume the caller is the creator.
            if not getattr(self, "caller", None):
                raise XOSProgrammingError("RCORDSubscriber's self.caller was not set")
            self.creator = self.caller

        # validate MAC Address
        if hasattr(self, 'mac_address') and self.mac_address:
            if not re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", self.mac_address.lower()):
                raise XOSValidationError("The MAC address specified is not valid: %s" % self.mac_address)

        self.set_owner()

        if self.status != "pre-provisioned" and \
                hasattr(self.owner.leaf_model, "access") and \
                self.owner.leaf_model.access == "voltha" and \
                not self.deleted:

            # if the access network is managed by voltha, validate that onu_device actually exist
            # we assume RCORDService is connected only to the vOLTService
            for ps in self.owner.provider_services:
                provider_service = ps.leaf_model
                if provider_service.name.lower() == "volt":
                    volt_service = provider_service
                    # When interacting with VOLT-service remove the -X from onu_device
                    if not volt_service.has_access_device(self.onu_device.split('-')[0]):
                       raise XOSValidationError("The onu_device you specified (%s) does not exists" % self.onu_device)

        super(RCORDSubscriber, self).save(*args, **kwargs)
        self.invalidate_related_objects()
        return

