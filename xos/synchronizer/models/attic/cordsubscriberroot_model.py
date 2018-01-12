
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


# 'simple_attributes' will be expanded into properties and setters that
# store the attribute using self.set_attribute / self.get_attribute.

simple_attributes = ( ("devices", []), )

sync_attributes = ("firewall_enable",
                   "firewall_rules",
                   "url_filter_enable",
                   "url_filter_rules",
                   "cdn_enable",
                   "uplink_speed",
                   "downlink_speed",
                   "enable_uverse",
                   "status")

def __init__(self, *args, **kwargs):
    # TODO: Should probably make an RCORDService, rather than filtering by name
    rcord_services = Service.objects.filter(name="rcord")
    if not rcord_services:
        # this isn't going to end well...
        raise Exception("There is no rcord service to use as the default service for CordSubscriberRoot")

    self._meta.get_field("owner").default = rcord_services[0].id

    super(CordSubscriberRoot, self).__init__(*args, **kwargs)

def find_device(self, mac):
    for device in self.devices:
        if device["mac"] == mac:
            return device
    return None

def update_device(self, mac, **kwargs):
    # kwargs may be "level" or "mac"
    #    Setting one of these to None will cause None to be stored in the db
    devices = self.devices
    for device in devices:
        if device["mac"] == mac:
            for arg in kwargs.keys():
                device[arg] = kwargs[arg]
            self.devices = devices
            return device
    raise ValueError("Device with mac %s not found" % mac)

def create_device(self, **kwargs):
    if "mac" not in kwargs:
        raise XOSMissingField("The mac field is required")

    if self.find_device(kwargs['mac']):
            raise XOSDuplicateKey("Device with mac %s already exists" % kwargs["mac"])

    device = kwargs.copy()

    devices = self.devices
    devices.append(device)
    self.devices = devices

    return device

def delete_device(self, mac):
    devices = self.devices
    for device in devices:
        if device["mac"]==mac:
            devices.remove(device)
            self.devices = devices
            return

    raise ValueError("Device with mac %s not found" % mac)

#--------------------------------------------------------------------------
# Deprecated -- devices used to be called users

def find_user(self, uid):
    return self.find_device(uid)

def update_user(self, uid, **kwargs):
    return self.update_device(uid, **kwargs)

def create_user(self, **kwargs):
    return self.create_device(**kwargs)

def delete_user(self, uid):
    return self.delete_user(uid)

# ------------------------------------------------------------------------

@property
def services(self):
    return {"cdn": self.cdn_enable,
            "url_filter": self.url_filter_enable,
            "firewall": self.firewall_enable}

@services.setter
def services(self, value):
    pass

def invalidate_related_objects(self):
    # Dirty all vSGs related to this subscriber, so the vSG synchronizer
    # will run.

    # TODO: This should be reimplemented when multiple-objects-per-synchronizer is implemented.

    for link in self.subscribed_links.all():
        outer_service_instance = link.provider_service_instance
        for link in outer_service_instance.subscribed_links.all():
            inner_service_instance = link.provider_service_instance
            inner_service_instance.save(update_fields = ["updated"])

def __xos_save_base(self, *args, **kwargs):
    self.validate_unique_service_specific_id(none_okay=True)
    if (not hasattr(self, 'caller') or not self.caller.is_admin):
        if (self.has_field_changed("service_specific_id")):
            raise XOSPermissionDenied("You do not have permission to change service_specific_id")

    super(CordSubscriberRoot, self).save(*args, **kwargs)

    self.invalidate_related_objects()

    return True     # Indicate that we called super.save()
