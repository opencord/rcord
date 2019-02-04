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


from xossynchronizer.modelaccessor import ServiceInstanceLink, model_accessor
from xossynchronizer.model_policies.policy import Policy

class RCORDSubscriberPolicy(Policy):
    model_name = "RCORDSubscriber"

    def handle_create(self, si):
        return self.handle_update(si)

    def handle_update(self, si):

        if si.status == "pre-provisioned":
            self.logger.debug("MODEL_POLICY: Skipping chain creation as RCORDSubscriber %s is in 'pre-provisioned' state" % si.id)
            return

        chain = si.subscribed_links.all()

        # Already has a chain
        if len(chain) > 0:
            self.logger.debug("MODEL_POLICY: RCORDSubscriber %s is already part of a chain" % si.id)
            if si.status == "awaiting-auth" or si.status == "auth-failed" or si.status == "disabled":
                # delete chain
                self.logger.debug("MODEL_POLICY: deleting RCORDSubscriber chain from %s" % si.id, status=si.status)
                for link in chain:
                    self.logger.debug("Removing link %s" % link.id, provider_service=link.provider_service_instance.leaf_model, subscriber_service=link.subscriber_service_instance.leaf_model)
                    link.delete()
                    link.provider_service_instance.leaf_model.delete()

        else:
            if si.status != "enabled":
                self.logger.debug("MODEL_POLICY: NOT creating RCORDSubscriber chain for %s" % si.id, status=si.status)
            else:
                self.logger.debug("MODEL_POLICY: creating RCORDSubscriber chain for %s" % si.id, status=si.status)
                # if it does not have a chain,
                # Find links to the next element in the service chain
                # and create one
                links = si.owner.subscribed_dependencies.all()

                for link in links:
                    si_class = link.provider_service.get_service_instance_class_name()
                    self.logger.info("MODEL_POLICY: RCORDSubscriber %s creating %s" % (si, si_class))

                    eastbound_si_class = model_accessor.get_model_class(si_class)
                    eastbound_si = eastbound_si_class()
                    eastbound_si.owner_id = link.provider_service_id
                    eastbound_si.save()
                    link = ServiceInstanceLink(provider_service_instance=eastbound_si, subscriber_service_instance=si)
                    link.save()

    def handle_delete(self, si):
        pass
