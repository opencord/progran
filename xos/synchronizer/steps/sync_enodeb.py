
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
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncStep
from synchronizers.new_base.modelaccessor import ENodeB

from xosconfig import Config
from multistructlog import create_logger
import json
import requests
from requests.auth import HTTPBasicAuth

log = create_logger(Config().get('logging'))

parentdir = os.path.join(os.path.dirname(__file__), "..")

sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.dirname(__file__))

from helpers import ProgranHelpers

class SyncProgranEnodeB(SyncStep):
    provides = [ENodeB]

    observes = ENodeB

    def get_progran_enodeb_field(self, o):

        enodeb = {
            "eNBId": o.enbId,
	        "Description": o.description,
	        "IpAddr": o.ipAddr
        }
        return enodeb

    def sync_record(self, o):
        log.info("sync'ing enodeb", object=str(o), **o.tologdict())

        onos = ProgranHelpers.get_progran_onos_info()

        enodeb_url = "http://%s:%s/onos/progran/enodeb/" % (onos['url'], onos['port'])
        data = self.get_progran_enodeb_field(o)
        log.debug("Sync'ing enodeb with data", request_data=data)

        if o.previously_sync == False:
            log.debug("Sending POST", url=enodeb_url, data=json.dumps(data))
            r = requests.post(enodeb_url, data=json.dumps(data), auth=HTTPBasicAuth(onos['username'], onos['password']))
        else:
            data = {
                "EnodeB": data
            }
            log.debug("Sending PUT", url=enodeb_url, data=json.dumps(data))
            r = requests.put(enodeb_url, data=json.dumps(data),
                              auth=HTTPBasicAuth(onos['username'], onos['password']))

        ProgranHelpers.get_progran_rest_errors(r)
        log.info("Enodeb synchronized", response=r.json())

        o.previously_sync = True
        o.save()

    def delete_record(self, o):
        log.info("deleting enodeb", object=str(o), **o.tologdict())
        onos = ProgranHelpers.get_progran_onos_info()
        enode_url = "http://%s:%s/onos/progran/enodeb/%s" % (onos['url'], onos['port'], o.enbId)
        r = requests.delete(enode_url, auth=HTTPBasicAuth(onos['username'], onos['password']))
        ProgranHelpers.get_progran_rest_errors(r)
        log.info("enodeb deleted", response=r.json())