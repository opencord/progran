
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

from synchronizers.new_base.SyncInstanceUsingAnsible import SyncStep
from synchronizers.new_base.modelaccessor import ProgranServiceInstance, ENodeB, Handover

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

class SyncProgranServiceInstanceBack(SyncStep):
    provides = [ProgranServiceInstance]

    observes = ProgranServiceInstance


    def call(self, failed=[], deletion=False):
        """
        Read profile from progran and save them in xos
        """

        if deletion == False:
            # NOTE we won't it to run only after the delete has completed
            return

        log.info("Reading profiles from progran")
        onos = ProgranHelpers.get_progran_onos_info()
        profile_url = "http://%s:%s/onos/progran/profile/" % (onos['url'], onos['port'])
        r = requests.get(profile_url, auth=HTTPBasicAuth(onos['username'], onos['password']))
        res = r.json()['ProfileArray']

        # remove default profiles
        res = [p for p in res if "Default" not in p['Name']]

        field_mapping = {
            'Name': 'name',
            'Start': 'start',
            'End': 'end'
        }

        field_transformations = {
            'Start': ProgranHelpers.date_to_time,
            'End': ProgranHelpers.date_to_time
        }

        handover_mapping = {
            'A5Hysteresis': 'HysteresisA5',
            'A3Hysteresis': 'HysteresisA3'
        }

        updated_profiles = []

        for p in res:

            # checking for handovers
            handover_dict = p['Handover']
            handover_dict = ProgranHelpers.convert_keys(handover_dict, handover_mapping)
            del p['Handover']

            try:
                handover = Handover.objects.get(**handover_dict)
                log.info("handover already exists, updating it", handover=handover_dict)
            except IndexError:
                handover = Handover()
                handover = ProgranHelpers.update_fields(handover, handover_dict)
                log.info("handover is new, creating it", handover=handover_dict)

            handover.save()

            # checking for profiles
            try:
                si = ProgranServiceInstance.objects.get(name=p['Name'])
                log.info("Profile %s already exists, updating it" % p['Name'])
            except IndexError:
                si = ProgranServiceInstance()
                si.name = p['Name']

                si.no_sync = True

                log.info("Profile %s is new, creating it" % p['Name'])

            si = ProgranHelpers.update_fields(si, p, field_mapping, field_transformations)
            si.handover = handover

            si.save()

            updated_profiles.append(si.name)

        existing_profiles = [p.name for p in ProgranServiceInstance.objects.all() if not p.is_new]
        deleted_profiles = ProgranHelpers.list_diff(existing_profiles, updated_profiles)

        if len(deleted_profiles) > 0:
            log.info("Profiles %s have been removed in progran, removing them from XOS" % str(deleted_profiles))
            for p in deleted_profiles:
                si = ProgranServiceInstance.objects.get(name=p)
                si.delete()
