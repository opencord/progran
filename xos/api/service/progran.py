
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


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.progran.models import *
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
import json

BASE_NAME = 'progran'


class VProgranProfileSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    uiid = serializers.CharField(required=False)
    profile = serializers.CharField(required=False)
    dlrate = serializers.CharField(required=False)
    ulrate = serializers.CharField(required=False)


    class Meta:
        model = VProgranProfile
        fields = ('uiid','id', 'profile', 'dlrate' , 'ulrate')




class VProgranImsiSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    uiid = serializers.CharField(required=False)
    imsi = serializers.CharField(required=False)
    profile  = serializers.CharField(required=False)


    class Meta:
        model = VProgranImsi
        fields = ('uiid','id', 'imsi', "profile")


class ProgranProfileViewSet(XOSViewSet):
    base_name = "progran"
    method_name = "profile"
    method_kind = "viewset"
    queryset = VProgranProfile.objects.all()
    serializer_class = VProgranProfileSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ProgranProfileViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def list(self, request):
        object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(object_list, many=True)

        return Response(serializer.data)


class ProgranImsiViewSet(XOSViewSet):
    base_name = "progran"
    method_name = "imsi"
    method_kind = "viewset"
    queryset = VProgranImsi.objects.all()
    serializer_class = VProgranImsiSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(ProgranImsiViewSet, self).get_urlpatterns(api_path=api_path)

        return patterns

    def list(self, request):
        object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(object_list, many=True)

        return Response(serializer.data)