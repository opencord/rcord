
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
from django.core.exceptions import ObjectDoesNotExist
from xos.exceptions import XOSValidationError, XOSProgrammingError, XOSPermissionDenied, XOSConfigurationError
from models_decl import RCORDService_decl, RCORDSubscriber_decl, RCORDIpAddress_decl, BandwidthProfile_decl

range_of_tags = list(range(16,4096))

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

    def generate_s_tag(self):

        # unused_s_tags_for_c_tag() this function will return a list of unused s_tags for that c_tag

        tag = random.choice(self.unused_s_tags_for_c_tag())

        # Check that combination(c_tag,s_tag) is unique.
        # If the combination is not unique it will keep on calling this function recursively till it gets a unique combination.

        self.s_tag = tag
        if None != self.get_used_s_c_tag_subscriber_id():
            return self.generate_s_tag()
        else:
            return tag

    def generate_c_tag(self):

        # unused_c_tags_for_s_tag() this function will return a list of unused c_tags for the given s_tag

        tag = random.choice(self.unused_c_tags_for_s_tag())

        # Check that this random generated value is valid across given ONU-first check.
        # If the value is valid it will assign c_tag wth it and do second check.
        # If the value is not valid below function is recursively called till it gets a unique value.

        if tag in self.get_used_c_tags():
            return self.generate_c_tag()
        else:
            self.c_tag = tag

        # Scenario if we don't have a s_tag.
        # Second check-verify that combination is unique across.

        if not self.s_tag:
            self.s_tag = self.generate_s_tag()
            return tag
        elif None != self.get_used_s_c_tag_subscriber_id():
            return self.generate_c_tag()
        else:
            return tag

    def unused_c_tags_for_s_tag(self):

        #This function will return a list of unused c_tags

        #If there is no s_tag
        global range_of_tags

        #If there's a s_tag, then return unused c_tags for that s_tag
        subscribers_with_same_s_tag = RCORDSubscriber.objects.filter(s_tag = self.s_tag)
        used_c_tags = [s.c_tag for s in subscribers_with_same_s_tag]
        if len(used_c_tags) == 0:
            return range_of_tags
        else:
            list_of_unused_c_tags_for_s_tag = list(set(range_of_tags) - set(used_c_tags))
            if len(list_of_unused_c_tags_for_s_tag) == 0:
                raise XOSConfigurationError("All the c_tags are exhausted for this s_tag: %s"% self.s_tag)
            else:
                return list_of_unused_c_tags_for_s_tag

    def unused_s_tags_for_c_tag(self):

        #This function will return a list of unused s_tags

        global range_of_tags
        #If there's a c_tag, then return unused s_tags for that c_tag
        subscribers_with_same_c_tag = RCORDSubscriber.objects.filter(c_tag = self.c_tag)
        used_s_tags = [s.s_tag for s in subscribers_with_same_c_tag]
        if len(used_s_tags) == 0:
            return range_of_tags
        else:
            list_of_unused_s_tags_for_c_tag = list(set(range_of_tags) - set(used_s_tags))
            if len(list_of_unused_s_tags_for_c_tag) == 0:
                raise XOSConfigurationError("All the s_tags are exhausted for this c_tag: %s"% self.c_tag)
            else:
                return list_of_unused_s_tags_for_c_tag
    def get_same_onu_subscribers(self):
        return RCORDSubscriber.objects.filter(onu_device=self.onu_device)

    def get_same_s_c_tag_subscribers(self):
        return RCORDSubscriber.objects.filter(c_tag=self.c_tag, s_tag=self.s_tag)

    def get_used_c_tags(self):
        same_onu_subscribers = self.get_same_onu_subscribers()
        same_onu_subscribers = [s for s in same_onu_subscribers if s.id != self.id]
        used_tags = [s.c_tag for s in same_onu_subscribers]
        return used_tags

    def get_used_s_c_tag_subscriber_id(self):
        # Function to check c_tag and s_tag combination are unique across.
        same_s_c_tag_subscribers = self.get_same_s_c_tag_subscribers()
        same_s_c_tag_subscribers = [s for s in same_s_c_tag_subscribers if s.id != self.id]
        if len(same_s_c_tag_subscribers) > 0:
            return same_s_c_tag_subscribers[0].id
        else:
            return None

    def validate_tech_profile_id(self):
        if self.owner.leaf_model.access != "voltha":
            # if we're not using VOLTHA we don't need to validate this
            return True

        volt = None
        for ps in self.owner.provider_services:
            provider_service = ps.leaf_model
            if provider_service.name.lower() == "volt":
                volt = provider_service

        # When interacting with VOLT-service remove the -X from onu_device
        technology = volt.get_olt_technology_from_unu_sn(self.onu_device.split('-')[0])

        try:
            tp = volt.get_tech_profile(technology, self.tech_profile_id)
            return True
        except ObjectDoesNotExist:
            return False


    def save(self, *args, **kwargs):
        self.validate_unique_service_specific_id(none_okay=True)

        # VSGServiceInstance will extract the creator from the Subscriber, as it needs a creator to create its
        # Instance.
        if not self.creator:
            # If we weren't passed an explicit creator, then we will assume the caller is the creator.
            if not getattr(self, "caller", None):
                raise XOSProgrammingError("RCORDSubscriber's self.caller was not set")
            self.creator = self.caller

        # validate MAC Address
        if hasattr(self, 'mac_address') and self.mac_address:
            if not re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", self.mac_address.lower()):
                raise XOSValidationError("The MAC address specified is not valid: %s" % self.mac_address)

        # validate c_tag
        if self.c_tag:
            is_update_with_same_tag = False

            if not self.is_new:
                # if it is an update, but the tag is the same, skip validation
                existing = RCORDSubscriber.objects.filter(id=self.id)

                if len(existing) > 0 and existing[0].c_tag == self.c_tag and existing[0].id == self.id:
                    is_update_with_same_tag = True

            if self.c_tag in self.get_used_c_tags() and not is_update_with_same_tag:
                raise XOSValidationError(
                    "The c_tag you specified (%s) has already been used on device %s" %
                    (self.c_tag, self.onu_device))

        # validate s_tag and c_tag combination
        if self.c_tag and self.s_tag:
            is_update_with_same_tag = False

            if not self.is_new:
                # if it is an update, but the tags are the same, skip validation
                existing = RCORDSubscriber.objects.filter(id=self.id)
                if len(existing) > 0 and existing[0].c_tag == self.c_tag and existing[0].s_tag == self.s_tag and existing[0].id == self.id:
                    is_update_with_same_tag = True

            id = self.get_used_s_c_tag_subscriber_id()
            if None != id and not is_update_with_same_tag:
                raise XOSValidationError("The c_tag(%s) and s_tag(%s) pair you specified,has already been used by Subscriber with Id (%s)" % (self.c_tag,self.s_tag,id))


        if not self.c_tag:
            self.c_tag = self.generate_c_tag()

        elif not self.s_tag:
            self.s_tag = self.generate_s_tag()

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

            # if the access network is managed by voltha, validate that the tech_profile_id actually exists
            if not self.validate_tech_profile_id():
                raise XOSValidationError("The technology profile you specified [%s] does not exist" % self.tech_profile_id)

        super(RCORDSubscriber, self).save(*args, **kwargs)
        self.invalidate_related_objects()
        return

