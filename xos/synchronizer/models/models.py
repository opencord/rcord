
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
import random
import socket
from django.core.exceptions import ObjectDoesNotExist
from xos.exceptions import XOSValidationError, XOSProgrammingError, XOSPermissionDenied, XOSConfigurationError
from models_decl import RCORDService_decl, RCORDSubscriber_decl, RCORDIpAddress_decl, BandwidthProfile_decl, RCORDUniTagInformation_decl

range_of_tags = list(range(16, 4096))

class RCORDUniTagInformation(RCORDUniTagInformation_decl):

    class Meta:
        proxy = True

    def validate_c_tag(self):
        if self.pon_c_tag and self.pon_c_tag not in range_of_tags:
            raise XOSValidationError("PON C-TAG out of range [16,4095]")
        # TODO: validate c_tag
        return True

    def validate_pair_c_s_tag(self):
        if self.pon_s_tag and self.pon_s_tag not in range_of_tags:
            raise XOSValidationError("PON S-TAG out of range [16,4095]")
        # TODO: validate s-c tag pair
        return True

    def validate_tech_profile_id(self):
        sub = self.subscriber
        print "SUB", sub
        print sub.owner.leaf_model
        print str(sub.owner.leaf_model.access)
        if hasattr(sub.owner.leaf_model, "access") and \
                sub.owner.leaf_model.access != "voltha" and \
                not self.deleted:
            # if we're not using VOLTHA we don't need to validate this
            return True

        volt = None
        for ps in sub.owner.provider_services:
            provider_service = ps.leaf_model
            if provider_service.name.lower() == "volt":
                volt = provider_service

        # When interacting with VOLT-service remove the -X from onu_device
        technology = volt.get_olt_technology_from_unu_sn(sub.onu_device.split('-')[0])
        try:
            tp = volt.get_tech_profile(technology, self.tech_profile_id)
            return True
        except ObjectDoesNotExist:
            return False

    def generate_s_tag(self):

        # unused_s_tags_for_c_tag() this function will return a list of unused s_tags for that c_tag
        tag = random.choice(self.unused_s_tags_for_c_tag())

        # Check that combination(c_tag,s_tag) is unique.
        # If the combination is not unique it will keep on calling this function recursively till it gets a unique combination.
        self.pon_s_tag = tag
        if self.used_s_c_tag_different_subscriber():
            return self.generate_s_tag()
        else:
            return tag

    def generate_c_tag(self):

        # unused_c_tags_for_s_tag() this function will return a list of unused c_tags for the given s_tag
        tag = random.choice(self.unused_c_tags_for_s_tag())

        # First check: Check that this random generated value is valid across given ONU.
        # If the value is valid it will assign pon_c_tag with it and do the second check.
        # If the value is not valid below function is recursively called till it gets a unique value.
        if tag in self.get_used_c_tags():
            return self.generate_c_tag()
        else:
            self.pon_c_tag = tag

        # Second check: verify that combination is unique across.
        # If we don't have an s_tag then generate it.
        if not self.pon_s_tag:
            self.pon_s_tag = self.generate_s_tag()
            return tag
        # If we have an s_tag, check that combination (c_tag,s_tag) is unique.
        if self.used_s_c_tag_different_subscriber():
            return self.generate_c_tag()
        else:
            return tag

    def unused_c_tags_for_s_tag(self):
        #This function will return a list of unused c_tags

        #If there is no s_tag
        global range_of_tags

        #If there's a s_tag, then return unused c_tags for that s_tag
        tag_info_same_s_tag = RCORDUniTagInformation.objects.filter(pon_s_tag = self.pon_s_tag)
        used_c_tags = [s.pon_c_tag for s in tag_info_same_s_tag]
        if len(used_c_tags) == 0:
            return range_of_tags
        else:
            list_of_unused_c_tags_for_s_tag = list(set(range_of_tags) - set(used_c_tags))
            if len(list_of_unused_c_tags_for_s_tag) == 0:
                raise XOSConfigurationError("All the pon_c_tags are exhausted for this s_tag: %s"% self.pon_s_tag)
            else:
                return list_of_unused_c_tags_for_s_tag

    def unused_s_tags_for_c_tag(self):

        #This function will return a list of unused s_tags

        global range_of_tags
        #If there's a c_tag, then return unused s_tags for that c_tag
        tag_info_same_c_tag = RCORDUniTagInformation.objects.filter(pon_c_tag = self.pon_c_tag)
        used_s_tags = [s.pon_s_tag for s in tag_info_same_c_tag]
        if len(used_s_tags) == 0:
            return range_of_tags
        else:
            list_of_unused_s_tags_for_c_tag = list(set(range_of_tags) - set(used_s_tags))
            if len(list_of_unused_s_tags_for_c_tag) == 0:
                raise XOSConfigurationError("All the pon_s_tags are exhausted for this c_tag: %s"% self.pon_c_tag)
            else:
                return list_of_unused_s_tags_for_c_tag

    def get_used_c_tags(self):
        """
        Retrieve the used C-tags for subscribers on the same ONU
        :return:
        """
        sub = self.subscriber
        same_onu_subscribers = []
        if sub:
            same_onu_subscribers = self.get_same_onu_subscribers(sub.onu_device)
        # Filter out current subscriber
        same_onu_subscribers = [s for s in same_onu_subscribers if s.id != self.subscriber_id]
        # Retrieve the Tags Information
        tag_info = []
        for s in same_onu_subscribers:
            tag_info.extend(s.unitaglist)
        used_tags = [t.pon_c_tag for t in tag_info]
        return used_tags

    def used_s_c_tag_different_subscriber(self):
        """
        Check if a combination (c_tag,s_tag) is used by a different subscriber
        :return:
        """
        same_tags = RCORDUniTagInformation.objects.filter(pon_c_tag=self.pon_c_tag, pon_s_tag=self.pon_s_tag)
        same_tags = [t for t in same_tags if t.subscriber_id != self.subscriber_id]
        if len(same_tags) > 0:
            return True
        return False

    def get_same_onu_subscribers(self, onu_device):
        return RCORDSubscriber.objects.filter(onu_device=onu_device)

    def save(self, *args, **kwargs):
        # TODO: check VLAN TAGs
        self.validate_c_tag()
        self.validate_pair_c_s_tag()

        if self.pon_c_tag is None:
            self.generate_c_tag()
        if self.pon_s_tag is None:
            self.generate_s_tag()

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

    def delete(self, *args, **kwargs):
        # Delete also the RCORDUniTagInformation entries connected to this Subscriber being deleted
        tags = RCORDUniTagInformation.objects.filter(subscriber=self.id)
        for tag in tags:
            tag.delete()
        super(RCORDSubscriber, self).delete(*args, **kwargs)
