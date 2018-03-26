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

import requests
from requests.auth import HTTPBasicAuth
import unittest
import json
from time import sleep

timeout = 10

baseUrl = 'http://10.128.22.3'
username = 'xosadmin@opencord.org'
password = '1UvlBSNmBCbqaHzTC8qV'

onosUrl = 'http://10.128.22.3:8183'
onosUser = 'karaf'
onosPass = 'karaf'

class ProgranTest(unittest.TestCase):

    # def test_connection(self):
    #     url = "%s/xosapi/v1/progran/progranserviceinstances" % baseUrl
    #     r = requests.get(url,  auth=HTTPBasicAuth(username, password))
    #     res = r.json()
    #     self.assertTrue(isinstance(res['items'], list))

    def test_create_profile(self):

        handover_id = None
        profile_id = None
        imsi_id = None
        enodeb_id = None

        print "\nCreate profile"

        # Create handover
        handover_data = {
            "A3offset": 2,
            "A5Thresh1Rsrp": 97,
            "A5Thresh1Rsrq": 10,
            "A5Thresh2Rsrp": 95,
            "A5Thresh2Rsrq": 8,
            "A5TriggerType": 0,
            "HysteresisA3": 1,
            "HysteresisA5": 1,
            "A3TriggerQuantity": 10,
            "A5TriggerQuantity": 20
        }

        handover_url = "%s/xosapi/v1/progran/handovers" % baseUrl
        hr = requests.post(handover_url, data=json.dumps(handover_data), auth=HTTPBasicAuth(username, password))
        handover_res = hr.json()
        handover_id = handover_res['id']
        self.assertEqual(handover_res['backend_code'], 0)

        # Create profile
        profile_data = {
            "name": "automated_test_1",
            "DlSchedType": "RR",
            "UlSchedType": "RR",
            "DlAllocRBRate": 20,
            "UlAllocRBRate": 20,
            "AdmControl": 1,
            "CellIndividualOffset": 1,
            "mmeip": "192.168.61.30",
            "mmeport": "36412",
            "SubsProfile": "",
            "DlWifiRate": 13,
            "DlUeAllocRbRate": 12,
            "handover_id": handover_id
        }

        profile_url = "%s/xosapi/v1/progran/progranserviceinstances" % baseUrl
        pr = requests.post(profile_url, data=json.dumps(profile_data), auth=HTTPBasicAuth(username, password))
        profile_res = pr.json()
        profile_id = profile_res['id']
        self.assertEqual(profile_res['backend_code'], 0)

        # Read profile from ONOS
        print "\nRead profile from ONOS"
        sleep(timeout)

        profile_read_url = "%s/onos/progran/profile/%s" % (onosUrl, profile_data['name'])
        pr = requests.get(profile_read_url, auth=HTTPBasicAuth(username, password))
        profile_read_res = pr.json()['ProfileArray'][0]
        self.assertEqual(profile_read_res['Name'], profile_data['name'])
        # TODO check for mme details

        print "\nAdd IMSI"
        # Add IMSI
        imsi_data = {
            "imsi_number": "302720100000421",
            "apn_number": "",
            "ue_status": 0
        }
        imsi_url = "%s/xosapi/v1/mcord/mcordsubscriberinstances" % baseUrl
        ir = requests.post(imsi_url, data=json.dumps(imsi_data), auth=HTTPBasicAuth(username, password))
        imsi_res = ir.json()
        imsi_id = imsi_res['id']
        self.assertEqual(imsi_res['backend_code'], 0)

        # Read IMSI and check status
        print "\nRead IMSI from ONOS"
        sleep(timeout)

        imsi_read_url = "%s/onos/progran/imsi/%s" % (onosUrl, imsi_data['imsi_number'])
        pr = requests.get(imsi_read_url, auth=HTTPBasicAuth(username, password))
        imsi_res = pr.json()['ImsiArray'][0]
        self.assertEqual(imsi_res['IMSI'], imsi_data['imsi_number'])

        # Add link from Profile to IMSI
        print "\nAdding imsi to profile"
        link_data = {
            "provider_service_instance_id": profile_id,
            "subscriber_service_instance_id": imsi_id,
        }
        link_url = "%s/xosapi/v1/core/serviceinstancelinks" % baseUrl
        ir = requests.post(link_url, data=json.dumps(link_data), auth=HTTPBasicAuth(username, password))
        link_res = ir.json()
        self.assertEqual(link_res['backend_code'], 0)

        # check link in ONOS
        print "\nRead IMSI Profiles from ONOS"
        sleep(timeout)
        imsi_profile_url = "%s/onos/progran/imsi/%s/profile" % (onosUrl, imsi_data['imsi_number'])
        pr = requests.get(imsi_profile_url, auth=HTTPBasicAuth(username, password))
        imsi_profile_res = pr.json()['ProfileArray'][0]
        self.assertEqual(imsi_profile_res['Name'], profile_data['name'])

        # Add EnodeB
        print "\nAdding Enodeb"
        enodeb_data = {
            "description": "testcem",
            "enbId": "402",
            "ipAddr": "192.168.32.1"
        }
        enodeb_url = "%s/xosapi/v1/progran/enodebs" % baseUrl
        r = requests.post(enodeb_url, data=json.dumps(enodeb_data), auth=HTTPBasicAuth(username, password))
        enodeb_res = r.json()
        enodeb_id = enodeb_res['id']
        self.assertEqual(enodeb_res['backend_code'], 0)

        # Check EnodeB in ONOS
        print "\nRead Enodeb from ONOS"
        sleep(timeout)

        enodeb_onos_url = "%s/onos/progran/enodeb/%s" % (onosUrl, enodeb_data['enbId'])
        pr = requests.get(enodeb_onos_url, auth=HTTPBasicAuth(username, password))
        enodeb_onos_res = pr.json()['EnodeBArray'][0]
        self.assertEqual(enodeb_onos_res['Description'], enodeb_data['description'])

        # Add enodeb to profile
        print "\n Adding EnodeB to profile"

        profile_data["enodeb_id"] = enodeb_id
        profile_update_url = "%s/%s" % (profile_url, profile_id)
        r = requests.put(profile_update_url, data=json.dumps(profile_data), auth=HTTPBasicAuth(username, password))
        update_res = r.json()

        # Check that enodeb has been added to profile
        print "\nRead Enodeb to profile from ONOS"
        sleep(timeout)

        enodeb_onos_url = "%s/onos/progran/enodeb/%s" % (onosUrl, enodeb_data['enbId'])
        pr = requests.get(enodeb_onos_url, auth=HTTPBasicAuth(username, password))
        enodeb_onos_res = pr.json()['EnodeBArray'][0]
        self.assertIn(profile_data['name'], enodeb_onos_res['ProfileArray'])

        # TODO change profile UL/DL rates in ONOS and check in XOS (how??)


if __name__ == "__main__":
    unittest.main()