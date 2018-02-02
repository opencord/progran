
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
from synchronizers.new_base.modelaccessor import ProgranServiceInstance, ENodeB, Handover

from xosconfig import Config
from multistructlog import create_logger
import json
import requests
from requests.auth import HTTPBasicAuth
import time
import datetime


log = create_logger(Config().get('logging'))

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.dirname(__file__))
from helpers import ProgranHelpers

class SyncProgranServiceInstance(SyncStep):
    provides = [ProgranServiceInstance]

    observes = ProgranServiceInstance

    # Poll every 5 loops of self.call
    poll = 0

    def sync_record(self, o):
        onos = ProgranHelpers.get_progran_onos_info()

        log.info("sync'ing profile", object=str(o), **o.tologdict())

        profile_url = "http://%s:%s/onos/progran/profile/" % (onos['url'], onos['port'])
        data = self.get_progran_profile_field(o)

        r = requests.post(profile_url, data=json.dumps(data), auth=HTTPBasicAuth(onos['username'], onos['password']))

        ProgranHelpers.get_progran_rest_errors(r)
        log.info("Profile synchronized", response=r.json())

        log.info("sync'ing enodeb", object=str(o), **o.tologdict())
        if o.enodeb_id:
            log.info("adding profile %s to enodeb %s" % (o.id, o.enodeb.enbId), object=str(o), **o.tologdict())
            enodeb_url = "http://%s:%s/onos/progran/enodeb/%s/profile" % (onos['url'], onos['port'], o.enodeb.enbId)
            data = {
                "ProfileArray": [
                    o.name
                ]
            }
            r = requests.post(enodeb_url, data=json.dumps(data), auth=HTTPBasicAuth(onos['username'], onos['password']))
            ProgranHelpers.get_progran_rest_errors(r)
            o.active_enodeb_id = o.enodeb_id # storing the value to know when it will be deleted
            log.info("EnodeB synchronized", response=r.json())
        elif o.active_enodeb_id:
            enb_id = ENodeB.objects.get(id=o.active_enodeb_id).enbId
            log.info("removing profile %s from enodeb %s" % (o.name, o.active_enodeb_id), object=str(o), **o.tologdict())
            enodeb_url = "http://%s:%s/onos/progran/enodeb/%s/profile/%s" % (onos['url'], onos['port'], enb_id, o.name)
            r = requests.delete(enodeb_url, auth=HTTPBasicAuth(onos['username'], onos['password']))
            ProgranHelpers.get_progran_rest_errors(r)
            o.active_enodeb_id = 0 # removing the value because it has been deleted
            log.info("EnodeB synchronized", response=r.json())

        o.save()

    def get_handover_for_profile(self, o):
        return {
            "A3Hysteresis": o.handover.HysteresisA3,
            "A3TriggerQuantity": o.handover.A3TriggerQuantity,
            "A3offset": o.handover.A3offset,
            "A5Hysteresis": o.handover.HysteresisA5,
            "A5Thresh1Rsrp": o.handover.A5Thresh1Rsrp,
            "A5Thresh1Rsrq": o.handover.A5Thresh1Rsrq,
            "A5Thresh2Rsrp": o.handover.A5Thresh2Rsrp,
            "A5Thresh2Rsrq": o.handover.A5Thresh2Rsrq,
            "A5TriggerQuantity": o.handover.A5TriggerQuantity,
        }

    def get_progran_profile_field(self, o):

        # basic information that we have in the service instance itself
        profile = {
            'AdmControl': o.AdmControl,
            "DlSchedType": o.DlSchedType,
            "Start": o.start, # TODO date has to be in the format dd.MM.yyyy HH:mm
            "UlSchedType": o.UlSchedType,
            "End": o.end, # TODO date has to be in the format dd.MM.yyyy HH:mm
            "CellIndividualOffset": o.CellIndividualOffset,
            "DlAllocRBRate": o.DlAllocRBRate,
            "Name": o.name,
            "UlAllocRBRate": o.UlAllocRBRate,
            "Handover": self.get_handover_for_profile(o),
            'mmeip': o.mmeip,
            'mmeport': o.mmeport,
            'DlWifiRate': o.DlWifiRate,
            'DlUeAllocRbRate': o.DlUeAllocRbRate,
        }

        return profile

    def delete_record(self, o):
        log.info("deleting profile", object=str(o), **o.tologdict())
        onos = ProgranHelpers.get_onos_info_from_si(o)
        profile_url = "http://%s:%s/onos/progran/profile/%s" % (onos['url'], onos['port'], o.name)
        r = requests.delete(profile_url, auth=HTTPBasicAuth(onos['username'], onos['password']))
        o.active_enodeb_id = 0  # removing the value because it has been deleted
        log.info("Profile synchronized", response=r.json())

    def fetch_pending(self, deleted):
        # self.read_profiles_from_progran()
        return super(SyncProgranServiceInstance, self).fetch_pending(deleted)

    @staticmethod
    def date_to_time(d):
        if len(d) == 0:
            return 0
        return time.mktime(datetime.datetime.strptime(d, "%d.%m.%Y %H:%S").timetuple())

    @staticmethod
    def update_fields(model, dict, mapping={}, transformations={}):
        dict = SyncProgranServiceInstance.convert_keys(dict, mapping, transformations)
        for k, v in dict.iteritems():
            if hasattr(model, k):
                setattr(model, k, v)
            else:
                log.warn("%s does not have a '%s' property, not updating it" % (model.model_name, k))
        return model

    @staticmethod
    def convert_keys(dict, mapping={}, transformations={}):
        for k, v in dict.iteritems():
            if k in mapping:
                # apply custom transformations to the data
                if k in transformations:
                    dict[k] = transformations[k](v)

                # NOTE we may have different names that the field in the dict
                dict[mapping[k]] = dict[k]
                del dict[k]
        return dict


    def my_call(self, failed=[], deletion=False):
        """
        Read profile from progran and save them in xos
        """
        if self.poll < 5:
            self.poll = self.poll + 1
        else:
            self.poll = 0
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
                'Start': SyncProgranServiceInstance.date_to_time,
                'End': SyncProgranServiceInstance.date_to_time
            }

            handover_mapping = {
                'A5Hysteresis': 'HysteresisA5',
                'A3Hysteresis': 'HysteresisA3'
            }

            for p in res:

                # checking for handovers
                handover_dict = p['Handover']
                handover_dict = SyncProgranServiceInstance.convert_keys(handover_dict, handover_mapping)
                del p['Handover']

                try:
                    handover = Handover.objects.get(**handover_dict)
                    log.info("handover already exists, updating it", handover=handover_dict)
                except IndexError:
                    handover = Handover()
                    handover = SyncProgranServiceInstance.update_fields(handover, handover_dict)
                    log.info("handover is new, creating it", handover=handover_dict)

                handover.save()

                # checking for profiles
                try:
                    si = ProgranServiceInstance.objects.get(name=p['Name'])
                    log.info("Profile %s already exists, updating it" % p['Name'])
                except IndexError:
                    si = ProgranServiceInstance()
                    si.name = p['Name']
                    log.info("Profile %s is new, creating it" % p['Name'])

                si = SyncProgranServiceInstance.update_fields(si, p, field_mapping, field_transformations)
                si.handover = handover



                # TODO keep track of the deleted profiles
                # existing profiles - updated profiles = deleted profiles

                si.save()
