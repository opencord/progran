
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
from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.modelaccessor import ProgranServiceInstance, ENodeB, Handover

from xosconfig import Config
from multistructlog import create_logger
import json
import requests
from requests.auth import HTTPBasicAuth
import time
import datetime


log = create_logger(Config().get('logging'))

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.dirname(__file__))
from helpers import ProgranHelpers

class SyncProgranServiceInstance(SyncStep):
    provides = [ProgranServiceInstance]

    observes = ProgranServiceInstance

    def sync_record(self, o):
        onos = ProgranHelpers.get_progran_onos_info()

        log.info("sync'ing profile", object=str(o), **o.tologdict())

        profile_url = "http://%s:%s/onos/progran/profile/" % (onos['url'], onos['port'])
        data = self.get_progran_profile_field(o)
        log.debug("Sync'ing profile with data", request_data=data)

        if o.previously_sync == False:
            log.debug("Sending POST", url=profile_url, data=json.dumps(data))
            r = requests.post(profile_url, data=json.dumps(data), auth=HTTPBasicAuth(onos['username'], onos['password']))
        else:
            log.debug("Sending PUT", url=profile_url, data=json.dumps(data))
            r = requests.put(profile_url, data=json.dumps(data),
                              auth=HTTPBasicAuth(onos['username'], onos['password']))

        ProgranHelpers.get_progran_rest_errors(r)
        log.info("Profile synchronized", response=r.json())

        if o.enodeb_id:
            log.info("adding profile %s to enodeb %s" % (o.id, o.enodeb.enbId), object=str(o), **o.tologdict())
            enodeb_url = "http://%s:%s/onos/progran/enodeb/%s/profile" % (onos['url'], onos['port'], o.enodeb.enbId)
            data = {
                "ProfileArray": [
                    o.name
                ]
            }
            log.debug("Adding enodeb to profile with data", request_data=data)
            r = requests.post(enodeb_url, data=json.dumps(data), auth=HTTPBasicAuth(onos['username'], onos['password']))
            ProgranHelpers.get_progran_rest_errors(r)
            o.active_enodeb_id = o.enodeb_id # storing the value to know when it will be deleted
            log.info("EnodeB synchronized", response=r.json())
        elif o.active_enodeb_id:
            enb_id = ENodeB.objects.get(id=o.active_enodeb_id).enbId
            log.info("removing profile %s from enodeb %s" % (o.name, o.active_enodeb_id), object=str(o), **o.tologdict())
            enodeb_url = "http://%s:%s/onos/progran/enodeb/%s/profile/%s" % (onos['url'], onos['port'], enb_id, o.name)
            r = requests.delete(enodeb_url, auth=HTTPBasicAuth(onos['username'], onos['password']))
            ProgranHelpers.get_progran_rest_errors(r)
            o.active_enodeb_id = 0 # removing the value because it has been deleted
            log.info("EnodeB synchronized", response=r.json())

        o.previously_sync = True
        o.save()

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
            "Start": o.start, # TODO date has to be in the format dd.MM.yyyy HH:mm
            "UlSchedType": o.UlSchedType,
            "End": o.end, # TODO date has to be in the format dd.MM.yyyy HH:mm
            "CellIndividualOffset": o.CellIndividualOffset,
            "DlAllocRBRate": o.DlAllocRBRate,
            "Name": o.name,
            "UlAllocRBRate": o.UlAllocRBRate,
            "Handover": self.get_handover_for_profile(o),
            "MMECfg": {
                "Port": o.mmeport,
                "IPAddr": o.mmeip,
            },
            'DlWifiRate': o.DlWifiRate,
            'DlUeAllocRbRate': o.DlUeAllocRbRate,
        }

        return profile

    def delete_record(self, o):
        log.info("deleting profile", object=str(o), **o.tologdict())
        onos = ProgranHelpers.get_onos_info_from_si(o)
        profile_url = "http://%s:%s/onos/progran/profile/%s" % (onos['url'], onos['port'], o.name)
        r = requests.delete(profile_url, auth=HTTPBasicAuth(onos['username'], onos['password']))
        o.active_enodeb_id = 0  # removing the value because it has been deleted
        log.info("Profile synchronized", response=r.json())

    def fetch_pending(self, deleted):
        return super(SyncProgranServiceInstance, self).fetch_pending(deleted)
