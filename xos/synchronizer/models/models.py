
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

from xos.exceptions import *
from models_decl import *
from core.models import Service

class CordSubscriberRoot(CordSubscriberRoot_decl):
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

    def save(self, *args, **kwargs):
        self.validate_unique_service_specific_id(none_okay=True)

        # NOTE setting owner_id
        try:
            rcord_service = Service.objects.filter(name="rcord")[0]
            self.owner_id = rcord_service.id
        except IndexError:
            raise XOSValidationError("Service RCORD cannot be found, please make sure that the model exists.")

        if (not hasattr(self, 'caller') or not self.caller.is_admin):
            if (self.has_field_changed("service_specific_id")):
                raise XOSPermissionDenied("You do not have permission to change service_specific_id")

        super(CordSubscriberRoot, self).save(*args, **kwargs)
        self.invalidate_related_objects()
        return