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

from xosconfig import Config
from multistructlog import create_logger
import time
import datetime

log = create_logger(Config().get('logging'))

class ProgranHelpers():

    @staticmethod
    def get_onos_info_from_si(service_instance):
        progran_service = service_instance.owner.leaf_model
        return ProgranHelpers.get_onos_info_from_service(progran_service)

    @staticmethod
    def get_progran_onos_info(model_accessor):
        try:
            progran_service = model_accessor.ProgranService.objects.all()[0]
        except IndexError:
            raise Exception("Cannot find Progran Service, does it exists?")
        return ProgranHelpers.get_onos_info_from_service(progran_service)

    @staticmethod
    def get_onos_info_from_service(progran_service):
        return {
            'url': progran_service.onos_address,
            'port': progran_service.onos_port,
            'username': progran_service.onos_username,
            'password': progran_service.onos_password,
        }

    @staticmethod
    def get_progran_rest_errors(res):
        res = res.json()
        if res['Result'] == -2 or res['Result'] == -1:
            log.error('Error from ONOS Progran', error=res)
            raise Exception(res['ErrCode'])

    @staticmethod
    def date_to_time(d):
        if len(d) == 0:
            return 0
        return time.mktime(datetime.datetime.strptime(d, "%d.%m.%Y %H:%S").timetuple())

    @staticmethod
    def int_to_string(i):
        return str(i)

    @staticmethod
    def update_fields(model, dict, mapping={}, transformations={}):
        dict = ProgranHelpers.convert_keys(dict, mapping, transformations)
        for k, v in dict.iteritems():
            if hasattr(model, k):
                log.debug("Setting %s=%s on %s" % (k, v, model.model_name))
                setattr(model, k, v)
            # else:
            #     log.debug("%s does not have a '%s' property, not updating it" % (model.model_name, k))
        return model

    @staticmethod
    def convert_keys(dict, mapping={}, transformations={}):
        for k, v in dict.iteritems():
            if k in mapping:
                # apply custom transformations to the data
                if k in transformations:
                    dict[k] = transformations[k](v)

                # NOTE we may have different names than the field in the dict
                dict[mapping[k]] = dict[k]
                del dict[k]
        return dict

    @staticmethod
    def list_diff(first, second):
        second = set(second)
        return [item for item in first if item not in second]