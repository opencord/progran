
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
from synchronizers.new_base.modelaccessor import MCordSubscriberInstance

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

class SyncProgranIMSI(SyncStep):
    provides = [MCordSubscriberInstance]

    observes = MCordSubscriberInstance

    def get_progran_imsi_field(self, o):

        imsi = {
            "IMSI": o.imsi_number,
        }
        return imsi

    def sync_record(self, o):
        log.info("sync'ing imsi", object=str(o), **o.tologdict())
        onos = ProgranHelpers.get_progran_onos_info()
        imsi_url = "http://%s:%s/onos/progran/imsi/" % (onos['url'], onos['port'])
        data = self.get_progran_imsi_field(o)
        r = requests.post(imsi_url, data=json.dumps(data), auth=HTTPBasicAuth(onos['username'], onos['password']))

        ProgranHelpers.get_progran_rest_errors(r)
        log.info("Profile synchronized", response=r.json())

    def delete_record(self, o):
        log.info("deleting imsi", object=str(o), **o.tologdict())
        onos = ProgranHelpers.get_progran_onos_info()
        profile_url = "http://%s:%s/onos/progran/imsi/%s" % (onos['url'], onos['port'], o.imsi_number)
        r = requests.delete(profile_url, auth=HTTPBasicAuth(onos['username'], onos['password']))
        log.info("IMSI synchronized", response=r.json())