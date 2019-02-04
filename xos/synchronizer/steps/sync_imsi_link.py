
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
from xossynchronizer.steps.syncstep import SyncStep
from xossynchronizer.modelaccessor import MCordSubscriberInstance, ServiceInstanceLink, ProgranServiceInstance

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

class SyncProgranIMSILink(SyncStep):
    provides = [ServiceInstanceLink]

    observes = ServiceInstanceLink

    # NOTE Override the default fetch_pending method to receive on links between MCordSubscriberInstances and ProgranServiceInstances
    def fetch_pending(self, deleted):

        objs = super(SyncProgranIMSILink, self).fetch_pending(deleted)
        objs = list(objs)

        to_be_sync = []

        for link in objs:
            if link.provider_service_instance.leaf_model_name == "ProgranServiceInstance" and link.subscriber_service_instance.leaf_model_name == "MCordSubscriberInstance":
                to_be_sync.append(link)

        return to_be_sync

    def sync_record(self, o):

        if o.provider_service_instance.leaf_model_name == "ProgranServiceInstance" and o.subscriber_service_instance.leaf_model_name ==  "MCordSubscriberInstance":
            log.info("sync'ing link", object=str(o), **o.tologdict())

            onos = ProgranHelpers.get_progran_onos_info(self.model_accessor)

            profile_name = o.provider_service_instance.name
            imsi_number =  o.subscriber_service_instance.leaf_model.imsi_number

            data = {
                "IMSIRuleArray": [
                    imsi_number
                ]
            }

            url = "http://%s:%s/onos/progran/profile/%s/imsi" % (onos['url'], onos['port'], profile_name)

            r = requests.post(url, data=json.dumps(data), auth=HTTPBasicAuth(onos['username'], onos['password']))
            ProgranHelpers.get_progran_rest_errors(r)

    def delete_record(self, o):

        if o.provider_service_instance.leaf_model_name == "ProgranServiceInstance" and o.subscriber_service_instance.leaf_model_name ==  "MCordSubscriberInstance":
            log.info("deleting link", object=str(o), **o.tologdict())

            onos = ProgranHelpers.get_progran_onos_info(self.model_accessor)

            profile_name = o.provider_service_instance.name
            imsi_number =  o.subscriber_service_instance.leaf_model.imsi_number

            url = "http://%s:%s/onos/progran/profile/%s/%s" % (onos['url'], onos['port'], profile_name, imsi_number)

            r = requests.delete(url, auth=HTTPBasicAuth(onos['username'], onos['password']))
            ProgranHelpers.get_progran_rest_errors(r)