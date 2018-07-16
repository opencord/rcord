
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


import json
import time
import os
import sys
from synchronizers.new_base.eventstep import EventStep
from synchronizers.new_base.modelaccessor import RCORDService, RCORDSubscriber, Service, model_accessor

# from xos.exceptions import XOSValidationError

class SubscriberAuthEventStep(EventStep):
    topics = ["authentication.events"]
    technology = "kafka"

    def __init__(self, *args, **kwargs):
        super(SubscriberAuthEventStep, self).__init__(*args, **kwargs)

    # def get_oss_service(self, onu_serial_number, retry=0):
    #     try:
    #         onu = ONUDevice.objects.get(serial_number=onu_serial_number)
    #     except IndexError as e:
    #         self.log.info("onu.events: get_oss_service", retry=retry, max_onu_retry=self.max_onu_retry)
    #         if retry < self.max_onu_retry:
    #             self.log.info("onu.events: No ONUDevice with serial_number %s is present in XOS, keep trying" % onu_serial_number)
    #             time.sleep(10)
    #             return self.get_oss_service(onu_serial_number, retry + 1)
    #         else:
    #             raise Exception("onu.events: No ONUDevice with serial_number %s is present in XOS" % onu_serial_number)

    #     volt_service = onu.pon_port.olt_device.volt_service
    #     service = Service.objects.get(id=volt_service.id)
    #     osses = [s for s in service.subscriber_services if s.kind.lower() == "oss"]

    #     if len(osses) > 1:
    #         self.log.warn("onu.events: More than one OSS found for %s" % volt_service.name)
    #     try:
    #         return osses[0].leaf_model
    #     except IndexError as e:
    #         return None

    def get_subscriber(self, event):
        rcord_service = RCORDService.objects.first()
        olt_service = Service.objects.get(id=rcord_service.id).provider_services[0].leaf_model
        onu_sn = olt_service.get_onu_sn_from_openflow(event["switch_dp_ip"], event["uni_port_id"])
        if not onu_sn or onu_sn is None:
            self.log.exception("authentication.events: Cannot find onu serial number for this event", kafka_event=event)
            raise Exception("authentication.events: Cannot find onu serial number for this event")

        subscriber = RCORDSubscriber.objects.get(onu_device=onu_sn)
        # NOTE we may need a retry mechanism in case the subscriber is not there yet

        return subscriber

    def activate_subscriber(self, subscriber):
        subscriber.status = 'enabled'
        subscriber.save()

    def disable_subscriber(self, subscriber):
        subscriber.status = 'auth-failed'
        subscriber.save()

    def process_event(self, event):
        value = json.loads(event.value)

        subscriber = self.get_subscriber(value)
        if not subscriber:
            self.log.exception("authentication.events: Cannot find subscriber for this event", kafka_event=value)
            raise Exception("authentication.events: Cannot find subscriber for this event")

        if value["authentication_state"] == "APPROVED":
            self.activate_subscriber(subscriber)
            self.log.info("authentication.events: subscriber authenticated", subscriber=subscriber)
        if value["authentication_state"] == "DENIED":
            self.disable_subscriber(subscriber)
            self.log.info("authentication.events: subscriber authentication denied", subscriber=subscriber)

