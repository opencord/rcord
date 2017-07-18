from django.db import models
from django.db.models import *
from core.models import Service, ServiceInstance, XOSBase, Slice, Instance, Node, Image, User, Flavor, NetworkParameter, NetworkParameterType, Port, AddressPool, User
from core.models.xosbase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
import traceback
from xos.exceptions import *
from xosconfig import Config

class ConfigurationError(Exception):
    pass

CORD_SUBSCRIBER_KIND = "CordSubscriberRoot"

