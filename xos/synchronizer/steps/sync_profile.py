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


class SyncVProfileApp(SyncStep):
    provides = [VProgranProfile]

    observes = VProgranProfile

    requested_interval = 0

    def __init__(self, *args, **kwargs):
        super(SyncVProfileApp, self).__init__(*args, **kwargs)

    def get_onos_progran_addr(self):

        return "http://%s:%s/onos/" % ("10.6.0.1", "8183")

    def get_onos_progran_auth(self):

        return HTTPBasicAuth("onos", "rocks")

    def sync_record(self, app):

        logger.info("Sync'ing Edited vProgran Profile ")

        onos_addr = self.get_onos_progran_addr()

        data = {}
        data["profile"] = app.profile
        data["dlrate"] = app.dlrate
        data["ulrate"] = app.ulrate


        url = onos_addr + "progran/mwc/profile"

        print "POST %s for app %s" % (url, "Progran Imsi")

        auth = self.get_onos_progran_auth()
        r = requests.post(url, data=json.dumps(data), auth=auth)
        if (r.status_code != 200):
            print r
            raise Exception("Received error from progran app update (%d)" % r.status_code)

    def delete_record(self, app):
        logger.info("Deletion is not supported yet")

