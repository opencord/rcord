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
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline, TenantRootTenantInline, TenantRootPrivilegeInline
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
    inlines = (TenantRootPrivilegeInline) # VOLTTenantInline

    suit_form_tabs =(('general', 'Cord Subscriber Root Details'),
#        ('volttenants','VOLT Tenancy'),
        ('tenantrootprivileges','Privileges')
    )

    def get_queryset(self, request):
        return CordSubscriberRoot.get_tenant_objects_by_user(request.user)

admin.site.register(CordSubscriberRoot, CordSubscriberRootAdmin)
