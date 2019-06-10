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

        chain = si.subscribed_links.all()

        # Already has a chain
        if si.status != "enabled" and len(chain) > 0:
            # delete chain
            self.logger.debug("MODEL_POLICY: deleting RCORDSubscriber chain from %s" % si.id, status=si.status)
            for link in chain:
                self.logger.debug("Removing link %s" % link.id,
                                  provider_service=link.provider_service_instance.leaf_model,
                                  subscriber_service=link.subscriber_service_instance.leaf_model)
                link.delete()
                link.provider_service_instance.leaf_model.delete()

        elif si.status == "enabled":

            self.logger.debug("MODEL_POLICY: creating RCORDSubscriber chain for %s" % si.id, status=si.status)
            # if it does not have a chain,
            # Find links to the next element in the service chain
            # and create one
            links = si.owner.subscribed_dependencies.all()

            for link in links:
                si_class = link.provider_service.get_service_instance_class_name()
                self.logger.info("MODEL_POLICY: RCORDSubscriber %s creating %s" % (si, si_class))

                provider_service = link.provider_service.leaf_model

                valid_provider_service_instance = provider_service.validate_links(si)
                if not valid_provider_service_instance:
                    provider_service.acquire_service_instance(si)
                else:
                    for si in valid_provider_service_instance:
                        si.save(always_update_timestamp=True)

    def handle_delete(self, si):
        pass
