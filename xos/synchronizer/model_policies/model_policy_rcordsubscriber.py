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


from synchronizers.new_base.modelaccessor import VOLTServiceInstance, ServiceInstanceLink
from synchronizers.new_base.policy import Policy

class RCORDSubscriberPolicy(Policy):
    model_name = "CordSubscriberRoot"

    def handle_create(self, si):
        return self.handle_update(si)

    def handle_update(self, si):

        chain = si.subscribed_links.all()

        # Already has a chain
        if len(chain) > 0 and not si.is_new:
            self.logger.debug("MODEL_POLICY: Subscriber %s is already part of a chain" % si.id)
            return

        # if it does not have a chain,
        # Find links to the next element in the service chain
        # and create one

        links = si.owner.subscribed_dependencies.all()

        for link in links:
            ps = link.provider_service.leaf_model

            # FIXME we should use get_service_instance_class here to support the general case.
            # we don't know what the next service in the chain will be

            if ps.model_name is "VOLTService":
                volt = VOLTServiceInstance(name="volt-for-subscriber-%s" % si.id)
                volt.save()

                si_link = ServiceInstanceLink(
                    provider_service_instance=volt,
                    subscriber_service_instance=si
                )
                si_link.save()

        print links


    def handle_delete(self, si):
        pass
