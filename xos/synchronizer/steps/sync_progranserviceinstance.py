
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


import os
import sys
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from synchronizers.new_base.ansible_helper import run_template
from synchronizers.new_base.modelaccessor import ProgranService, ProgranServiceInstance

from xosconfig import Config
from multistructlog import create_logger
import json

log = create_logger(Config().get('logging'))

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncProgranServiceInstance(SyncInstanceUsingAnsible):
    provides = [ProgranServiceInstance]

    observes = ProgranServiceInstance

    def get_onos_info(self, si):

        progran_service = si.owner.leaf_model

        return {
            'url': progran_service.onos_address,
            'port': progran_service.onos_port,
            'username': progran_service.onos_username,
            'password': progran_service.onos_password,
        }

    def skip_ansible_fields(self, o):
        # FIXME This model does not have an instance, this is a workaroung to make it work,
        # but it need to be cleaned up creating a general SyncUsingAnsible base class
        return True

    def get_handover_for_profile(self, o):
        return {
            "A3Hysteresis": o.handover.HysteresisA3,
            "A3TriggerQuantity": o.handover.A3TriggerQuantity,
            "A3offset": o.handover.A3offset,
            "A5Hysteresis": o.handover.HysteresisA5,
            "A5Thresh1Rsrp": o.handover.A5Thresh1Rsrp,
            "A5Thresh1Rsrq": o.handover.A5Thresh1Rsrq,
            "A5Thresh2Rsrp": o.handover.A5Thresh2Rsrp,
            "A5Thresh2Rsrq": o.handover.A5Thresh2Rsrq,
            "A5TriggerQuantity": o.handover.A5TriggerQuantity,
        }

    def get_progran_profile_field(self, o):

        # basic information that we have in the service instance itself
        profile = {
            'AdmControl': o.AdmControl,
            "DlSchedType": o.DlSchedType,
            "Start": o.start,
            "UlSchedType": o.UlSchedType,
            "End": o.end,
            "CellIndividualOffset": o.CellIndividualOffset,
            "DlAllocRBRate": o.DlAllocRBRate,
            "Name": o.name,
            "UlAllocRBRate": o.UlAllocRBRate,
            "Handover": self.get_handover_for_profile(o),
        }
        profile = json.dumps(profile)
        return profile

    def get_extra_attributes(self, o):
        onos = self.get_onos_info(o)
        fields = {
            'onos_url': onos['url'],
            'onos_username': onos['username'],
            'onos_password': onos['password'],
            'onos_port': onos['port'],
            'endpoint': 'profile',
            'profile': self.get_progran_profile_field(o),
            'method': 'POST'
        }

        return fields

    # FIXME we need to override this as the default expect to ssh into a VM
    def run_playbook(self, o, fields):
        run_template("progran_curl.yaml", fields, object=o)

    def delete_record(self, o):
        log.info("deleting object", object=str(o), **o.tologdict())
        onos = self.get_onos_info(o)
        fields = {
            'onos_url': onos['url'],
            'onos_username': onos['username'],
            'onos_password': onos['password'],
            'onos_port': onos['port'],
            'endpoint': 'profile/%s' % o.name,
            'profile': '',
            'method': 'DELETE'
        }
        res = self.run_playbook(o, fields)