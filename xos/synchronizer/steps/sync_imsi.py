
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
from synchronizers.new_base.modelaccessor import MCordSubscriberInstance

from xosconfig import Config
from multistructlog import create_logger
import json
import requests


log = create_logger(Config().get('logging'))

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.dirname(__file__))
from helpers import ProgranHelpers

class SyncProgranIMSI(SyncInstanceUsingAnsible):
    provides = [MCordSubscriberInstance]

    observes = MCordSubscriberInstance

    def skip_ansible_fields(self, o):
        # FIXME This model does not have an instance, this is a workaroung to make it work,
        # but it need to be cleaned up creating a general SyncUsingAnsible base class
        return True

    def get_progran_imsi_field(self, o):

        imsi = {
            "IMSI": o.imsi_number,
        }
        imsi = json.dumps(imsi)
        return imsi

    def get_fields(self, o):
        onos = ProgranHelpers.get_progran_onos_info()
        fields = {
            'onos_url': onos['url'],
            'onos_username': onos['username'],
            'onos_password': onos['password'],
            'onos_port': onos['port'],
        }

        return fields

    def sync_record(self, o):
        # NOTE overriding the default method as we need to read from progran
        base_fields = self.get_fields(o)

        create_fields = {
            'endpoint': 'imsi',
            'body': self.get_progran_imsi_field(o),
            'method': 'POST'
        }

        create_fields["ansible_tag"] = getattr(o, "ansible_tag", o.__class__.__name__ + "_" + str(o.id))
        create_fields.update(base_fields)

        self.run_playbook(o, create_fields)

        # fetch the IMSI we just created
        # NOTE we won't need this method once we'll have polling in place
        imsi_url = "http://%s:%s/onos/progran/imsi/%s" % (base_fields['onos_url'], base_fields['onos_port'], o.imsi_number)
        r = requests.get(imsi_url)
        o.ue_status = r.json()['ImsiArray'][0]['UeStatus']

        o.save()

    # FIXME we need to override this as the default expect to ssh into a VM
    def run_playbook(self, o, fields):
        return run_template("progran_curl.yaml", fields, object=o)

    def delete_record(self, o):
        log.info("deleting object", object=str(o), **o.tologdict())
        onos = ProgranHelpers.get_progran_onos_info()
        fields = {
            'onos_url': onos['url'],
            'onos_username': onos['username'],
            'onos_password': onos['password'],
            'onos_port': onos['port'],
            'endpoint': 'imsi/%s' % o.imsi_number,
            'body': '',
            'method': 'DELETE'
        }
        res = self.run_playbook(o, fields)