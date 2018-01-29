
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
from synchronizers.new_base.modelaccessor import ENodeB

from xosconfig import Config
from multistructlog import create_logger
import json

from helpers import ProgranHelpers

log = create_logger(Config().get('logging'))

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncProgranEnodeB(SyncInstanceUsingAnsible):
    provides = [ENodeB]

    observes = ENodeB

    def skip_ansible_fields(self, o):
        # FIXME This model does not have an instance, this is a workaroung to make it work,
        # but it need to be cleaned up creating a general SyncUsingAnsible base class
        return True

    def get_progran_enodeb_field(self, o):

        enodeb = {
            "eNBId": o.enbId,
	        "Description": o.description,
	        "IpAddr": o.ipAddr
        }
        enodeb = json.dumps(enodeb)
        return enodeb

    def get_extra_attributes(self, o):
        onos = ProgranHelpers.get_progran_onos_info()
        fields = {
            'onos_url': onos['url'],
            'onos_username': onos['username'],
            'onos_password': onos['password'],
            'onos_port': onos['port'],
            'endpoint': 'enodeb',
            'profile': self.get_progran_enodeb_field(o),
            'method': 'POST'
        }

        return fields

    # FIXME we need to override this as the default expect to ssh into a VM
    def run_playbook(self, o, fields):
        run_template("progran_curl.yaml", fields, object=o)

    def delete_record(self, o):
        log.info("deleting object", object=str(o), **o.tologdict())
        onos = ProgranHelpers.get_progran_onos_info()
        fields = {
            'onos_url': onos['url'],
            'onos_username': onos['username'],
            'onos_password': onos['password'],
            'onos_port': onos['port'],
            'endpoint': 'enodeb/%s' % o.enbId,
            'profile': '',
            'method': 'DELETE'
        }
        res = self.run_playbook(o, fields)