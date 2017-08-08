
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


from django.contrib import admin

#from services.volt.models import *
from services.rcord.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline
from core.middleware import get_request

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

#class VOLTTenantInline(XOSTabularInline):
#    model = VOLTTenant
#    fields = ['provider_service', 'subscriber_root', 'service_specific_id']
#    readonly_fields = ['provider_service', 'subscriber_root', 'service_specific_id']
#    extra = 0
#    max_num = 0
#    suit_classes = 'suit-tab suit-tab-volttenants'
#    fk_name = 'subscriber_root'
#    verbose_name = 'subscribed tenant'
#    verbose_name_plural = 'subscribed tenants'
#
#    @property
#    def selflink_reverse_path(self):
#        return "admin:cord_volttenant_change"

class CordSubscriberRootForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (CordSubscriberRootForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = CORD_SUBSCRIBER_KIND

    def save(self, commit=True):
        return super(CordSubscriberRootForm, self).save(commit=commit)

    class Meta:
        model = CordSubscriberRoot
        fields = '__all__'

class CordSubscriberRootAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id',  'name', )
    list_display_links = ('backend_status_icon', 'id', 'name', )
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'name', 'service_specific_id', # 'service_specific_attribute',
                                     'url_filter_level', "uplink_speed", "downlink_speed", "status", "enable_uverse", "cdn_enable"],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'service_specific_attribute',)
    form = CordSubscriberRootForm

    suit_form_tabs =(('general', 'Cord Subscriber Root Details'),
#        ('volttenants','VOLT Tenancy'),
#        ('tenantrootprivileges','Privileges')
    )

    def get_queryset(self, request):
        return CordSubscriberRoot.get_tenant_objects_by_user(request.user)

admin.site.register(CordSubscriberRoot, CordSubscriberRootAdmin)
