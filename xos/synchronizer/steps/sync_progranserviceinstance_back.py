
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

from xossynchronizer.steps.syncstep import SyncStep
from xossynchronizer.modelaccessor import ProgranServiceInstance, ENodeB, Handover, ServiceInstanceLink, MCordSubscriberInstance

from xosconfig import Config
from multistructlog import create_logger
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

        log.debug("Reading profiles from progran")
        onos = ProgranHelpers.get_progran_onos_info(self.model_accessor)
        profile_url = "http://%s:%s/onos/progran/profile/" % (onos['url'], onos['port'])
        r = requests.get(profile_url, auth=HTTPBasicAuth(onos['username'], onos['password']))
        res = r.json()['ProfileArray']


        # remove default profiles
        res = [p for p in res if "Default" not in p['Name']]
        pnames = [p['Name'] for p in res]
        log.debug("Received Profiles: ", profiles=pnames)

        field_mapping = {
            'Name': 'name',
            'Start': 'start',
            'End': 'end',
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


            # checking for profiles
            try:
                si = ProgranServiceInstance.objects.get(name=p['Name'])
                log.debug("Profile %s already exists, updating it" % p['Name'])

            except IndexError:
                si = ProgranServiceInstance()

                si.created_by = "Progran"

                log.debug("Profile %s is new, creating it" % p['Name'])

            if not si.is_new:
                # update IMSI association
                xos_imsis_for_profile = [i.subscriber_service_instance.leaf_model for i in si.provided_links.all()]
                progran_imsis_for_profile = p['IMSIRuleArray']

                log.debug("List of imsis for profile %s in XOS" % p["Name"], imsis=xos_imsis_for_profile)
                log.debug("List of imsis for profile %s in ONOS" % p["Name"], imsis=progran_imsis_for_profile)

                for i in xos_imsis_for_profile:
                    if not i.imsi_number in progran_imsis_for_profile:
                        log.debug("Removing Imsi %s from profile %s" % (i.imsi_number, p['Name']))

                        imsi_link = ServiceInstanceLink.objects.get(subscriber_service_instance_id=i.id)

                        # NOTE: this model has already been removed from the backend, no need to synchronize
                        imsi_link.backend_need_delete = False
                        imsi_link.no_sync = True
                        imsi_link.save() # we need to save it to avoid a synchronization loop

                        imsi_link.delete()
                    else:
                        # remove from imsi list coming from progran everything we already know about
                        progran_imsis_for_profile.remove(i.imsi_number)

                for i in progran_imsis_for_profile:
                    log.debug("Adding Imsi %s to profile %s" % (i, p['Name']))
                    imsi = MCordSubscriberInstance.objects.get(imsi_number=i)
                    imsi_to_profile = ServiceInstanceLink(provider_service_instance=si,
                                                          subscriber_service_instance=imsi)
                    imsi_to_profile.save()

            # if the model has not been synchronized yet, skip it
            if not si.is_new and si.no_sync is False:
                log.debug("Skipping profile %s as not synchronized" % p['Name'])
                # NOTE add it to the removed profiles to avoid deletion (this is ugly, I know)
                updated_profiles.append(si.name)
                continue

            # ugly fix
            if 'AdmControl' in p.keys():
                p['AdmControl'] = str(p['AdmControl'])

            si = ProgranHelpers.update_fields(si, p, field_mapping, field_transformations)

            # checking for handovers
            handover_dict = p['Handover']
            handover_dict = ProgranHelpers.convert_keys(handover_dict, handover_mapping)
            del p['Handover']

            if si.handover_id:
                handover = si.handover
                log.debug("handover already exists, updating it", handover=handover_dict)
            else:
                handover = Handover()
                handover = ProgranHelpers.update_fields(handover, handover_dict)
                log.debug("handover is new, creating it", handover=handover_dict)
                handover.created_by = "Progran"

            handover = ProgranHelpers.update_fields(handover, handover_dict)
            handover.save()

            # Assigning handover to profile
            si.handover = handover

            # si.backend_status = "OK"
            # si.backend_code = 1

            si.no_sync = True
            si.previously_sync = True

            if p["MMECfg"]:
                si.mmeip = str(p["MMECfg"]["IPAddr"])
                si.mmeport = str(p["MMECfg"]["Port"])

            si.enacted = time.mktime(datetime.datetime.now().timetuple())

            si.save()

            updated_profiles.append(si.name)

        existing_profiles = [p.name for p in ProgranServiceInstance.objects.all() if not p.is_new]
        deleted_profiles = ProgranHelpers.list_diff(existing_profiles, updated_profiles)

        if len(deleted_profiles) > 0:
            for p in deleted_profiles:
                si = ProgranServiceInstance.objects.get(name=p)
                if si.created_by == 'XOS' and si.previously_sync == False:
                    # don't delete if the profile has been created by XOS and it hasn't been sync'ed yet
                    continue
                # TODO delete also the associated Handover
                log.debug("Profiles %s have been removed in progran, removing it from XOS" % str(p))
                si.delete()