from django.db import models
from core.models import Service, XOSBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber, NetworkParameter, NetworkParameterType, Port, AddressPool
from core.models.xosbase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
from core.models import Tag
from core.models.service import LeastLoadedNodeScheduler
import traceback
from xos.exceptions import *
from xos.config import Config


class ConfigurationError(Exception):
    pass


PROGRAN_KIND = "Progran"
APP_LABEL = "progran"



class VProgranService(Service):
    KIND = PROGRAN_KIND

    class Meta:
        app_label = APP_LABEL
        verbose_name = "Progran Service"
        proxy = True

    default_attributes = {
        "rest_hostname": "10.6.0.1",
        "rest_port": "8183",
        "rest_user": "onos",
        "rest_pass": "rocks"
    }

    @property
    def rest_hostname(self):
        return self.get_attribute("rest_hostname", self.default_attributes["rest_hostname"])

    @rest_hostname.setter
    def rest_hostname(self, value):
        self.set_attribute("rest_hostname", value)

    @property
    def rest_port(self):
        return self.get_attribute("rest_port", self.default_attributes["rest_port"])

    @rest_port.setter
    def rest_port(self, value):
        self.set_attribute("rest_port", value)

    @property
    def rest_user(self):
        return self.get_attribute("rest_user", self.default_attributes["rest_user"])

    @rest_user.setter
    def rest_user(self, value):
        self.set_attribute("rest_user", value)

    @property
    def rest_pass(self):
        return self.get_attribute("rest_pass", self.default_attributes["rest_pass"])




class VProgranImsi(XOSBase):
    class Meta:
        app_label = APP_LABEL
        verbose_name = "vProgran Imsi"

    uiid = models.IntegerField( help_text="uiid ", null=False, blank=False)
    imsi = models.CharField(max_length=20, help_text="imsi ", null=False, blank=False)
    profile = models.CharField(max_length=20, help_text="profile name", null=True, blank=True)


class VProgranProfile(XOSBase):

    class Meta:
        app_label = APP_LABEL
        verbose_name = "vProgran Profile"

    uiid = models.IntegerField( help_text="uiid ", null=False, blank=False)
    profile = models.CharField(max_length=20, help_text="profile name", null=False, blank=False)
    dlrate = models.IntegerField( help_text="device download rate", null=False, blank=False)
    ulrate = models.IntegerField( help_text="device upload rate", null=False, blank=False )

