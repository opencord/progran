
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

import datetime
import time

from xossynchronizer.steps.SyncInstanceUsingAnsible import SyncStep
from xossynchronizer.modelaccessor import MCordSubscriberInstance

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

class SyncImsiBack(SyncStep):
    provides = [MCordSubscriberInstance]

    observes = MCordSubscriberInstance


    def call(self, failed=[], deletion=False):
        """
        Read profile from progran and save them in xos
        """

        if deletion == False:
            # NOTE we won't it to run only after the delete has completed
            return

        log.debug("Reading IMSI from progran")
        onos = ProgranHelpers.get_progran_onos_info(self.model_accessor)
        imsi_url = "http://%s:%s/onos/progran/imsi/" % (onos['url'], onos['port'])
        r = requests.get(imsi_url, auth=HTTPBasicAuth(onos['username'], onos['password']))
        res = r.json()['ImsiArray']

        log.debug("Received IMSIs: ", imsis=res)

        field_mapping = {
            'IMSI': 'imsi_number',
            'UeStatus': 'ue_status'
        }

        updated_imsi = []

        for i in res:
            try:
                si = MCordSubscriberInstance.objects.get(imsi_number=i['IMSI'])
                log.debug("IMSI %s already exists, updating it" % i['IMSI'])
            except IndexError:
                si = MCordSubscriberInstance()

                si.no_sync = True
                si.backend_code = 1
                si.backend_status = "OK"
                si.created_by = "Progran"

                log.debug("IMSI %s is new, creating it" % i['IMSI'])

            si = ProgranHelpers.update_fields(si, i, field_mapping,)

            si.save()

            updated_imsi.append(si.imsi_number)

        existing_imsi = [p.imsi_number for p in MCordSubscriberInstance.objects.all() if not p.is_new]
        deleted_imsi = ProgranHelpers.list_diff(existing_imsi, updated_imsi)

        if len(deleted_imsi) > 0:
            log.debug("Profiles %s have been removed in progran, removing them from XOS" % str(deleted_imsi))
            for p in deleted_imsi:
                si = MCordSubscriberInstance.objects.get(imsi_number=p)
                # if si.created_by == 'XOS' and si.previously_sync == False:
                    # don't delete if the imsi has been created by XOS and it hasn't been sync'ed yet
                    # continue
                si.delete()
