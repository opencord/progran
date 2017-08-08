
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
import requests
import json
from django.db.models import Q, F
from services.progran.models import *
from synchronizers.base.syncstep import SyncStep
from xos.logger import Logger, logging

# from core.models import Service
from requests.auth import HTTPBasicAuth

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

logger = Logger(level=logging.INFO)


class SyncVImsiApp(SyncStep):
    provides = [VProgranImsi]

    observes = VProgranImsi

    requested_interval = 0

    def __init__(self, *args, **kwargs):
        super(SyncVImsiApp, self).__init__(*args, **kwargs)

    def get_onos_progran_addr(self):

        return "http://%s:%s/onos/" % ("10.6.0.1", "8183")

    def get_onos_progran_auth(self):

        return HTTPBasicAuth("onos", "rocks")

    def sync_record(self, app):

        logger.info("Sync'ing Edited vProgran Imsi")

        onos_addr = self.get_onos_progran_addr()

        data = {}
        data["imsi"] = app.imsi
        data["profile"] = app.profile


        url = onos_addr + "progran/mwc/connect"

        print "POST %s for app %s" % (url, "Progran Imsi")

        auth = self.get_onos_progran_auth()
        r = requests.post(url, data=json.dumps(data), auth=auth)
        if (r.status_code != 200):
            print r
            raise Exception("Received error from progran app update (%d)" % r.status_code)

    def delete_record(self, app):
        logger.info("Deletion is not supported yet")

