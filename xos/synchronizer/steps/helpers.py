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

from xosconfig import Config
from multistructlog import create_logger
from synchronizers.new_base.modelaccessor import ProgranService

log = create_logger(Config().get('logging'))

class ProgranHelpers():

    @staticmethod
    def get_onos_info_from_si(service_instance):
        progran_service = service_instance.owner.leaf_model
        return ProgranHelpers.get_onos_info_from_service(progran_service)

    @staticmethod
    def get_progran_onos_info():
        progran_service = ProgranService.objects.all()[0]
        return ProgranHelpers.get_onos_info_from_service(progran_service)

    @staticmethod
    def get_onos_info_from_service(progran_service):
        return {
            'url': progran_service.onos_address,
            'port': progran_service.onos_port,
            'username': progran_service.onos_username,
            'password': progran_service.onos_password,
        }
