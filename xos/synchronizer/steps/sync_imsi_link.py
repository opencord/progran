
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
from synchronizers.new_base.modelaccessor import MCordSubscriberInstance, ServiceInstanceLink

from xosconfig import Config
from multistructlog import create_logger
import json


log = create_logger(Config().get('logging'))

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.dirname(__file__))
from helpers import ProgranHelpers

class SyncProgranIMSILink(SyncInstanceUsingAnsible):
    provides = [ServiceInstanceLink]

    observes = ServiceInstanceLink

    def skip_ansible_fields(self, o):
        # FIXME This model does not have an instance, this is a workaroung to make it work,
        # but it need to be cleaned up creating a general SyncUsingAnsible base class
        return True

    def get_progran_imsi_field(self, o):

        imsi = {
            "IMSIRuleArray": [
                '123' # TODO retrieve it service_instance_link.subscriber_service_instance.imsi_number
            ]
        }
        imsi = json.dumps(imsi)
        return imsi

    def get_extra_attributes(self, o):


        return fields

    def sync_record(self, o):
        log.info("sync'ing profile", object=str(o), **o.tologdict())
        # onos = ProgranHelpers.get_progran_onos_info()
        # profile_name = 'foo' # TODO retrieve it service_instance_link.subscriber_service_instance.imsi_number
        #
        # fields = {
        #     'onos_url': onos['url'],
        #     'onos_username': onos['username'],
        #     'onos_password': onos['password'],
        #     'onos_port': onos['port'],
        #     'endpoint': 'profile/%s/imsi' % profile_name,
        #     'body': self.get_progran_imsi_field(o),
        #     'method': 'POST'
        # }
        # fields = {}
        # self.run_playbook(o, fields)
        # o.save()
        print o

    # FIXME we need to override this as the default expect to ssh into a VM
    def run_playbook(self, o, fields):
        run_template("progran_curl.yaml", fields, object=o)

    def delete_record(self, o):
        log.info("deleting object", object=str(o), **o.tologdict())
        # onos = ProgranHelpers.get_progran_onos_info()
        # profile_name = 'foo'
        # imsi_number = 'bar'
        # fields = {
        #     'onos_url': onos['url'],
        #     'onos_username': onos['username'],
        #     'onos_password': onos['password'],
        #     'onos_port': onos['port'],
        #     'endpoint': 'profile/{profile_name}/{imsi}' % (profile_name, imsi_number),
        #     'body': '',
        #     'method': 'DELETE'
        # }
        # self.run_playbook(o, fields)