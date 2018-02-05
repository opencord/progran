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

from xos.exceptions import XOSValidationError

from models_decl import ProgranService_decl
from models_decl import ENodeB_decl
from models_decl import Handover_decl
from models_decl import ProgranServiceInstance_decl

class ProgranService(ProgranService_decl):
    class Meta:
        proxy = True
    def save(self, *args, **kwargs):

        existing_services = ProgranService.objects.all()

        if len(existing_services) > 0 and not self.delete:
            raise XOSValidationError("A ProgranService already exists, you should not have more than one")

        super(ProgranService, self).save(*args, **kwargs)


class ENodeB(ENodeB_decl):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):

        # remove all the profiles related to this enodeb (clearing the relation, not the models)
        if self.deleted:
            self.profiles.clear()

        # prevent enbId duplicates
        try:
            instance_with_same_id = ENodeB.objects.get(enbId=self.enbId)

            if (not self.pk and instance_with_same_id) or (self.pk and self.pk != instance_with_same_id.pk):
                raise XOSValidationError("A ENodeB with enbId '%s' already exists" % self.enbId)
        except self.DoesNotExist:
            pass

        if self.is_new and not self.created_by:
            # NOTE if created_by is null it has been created by XOS
            self.created_by = "XOS"

        super(ENodeB, self).save(*args, **kwargs)


class Handover(Handover_decl):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if self.is_new and not self.created_by:
            # NOTE if created_by is null it has been created by XOS
            self.created_by = "XOS"
        super(Handover, self).save(*args, **kwargs)



class ProgranServiceInstance(ProgranServiceInstance_decl):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        # NOTE someone is setting owner_id, so just override it for now
        try:
            # NOTE we allow just one ProgranService
            progran_service = ProgranService.objects.all()[0]
            self.owner_id = progran_service.id
        except IndexError:
            raise XOSValidationError("Service Progran cannot be found, please make sure that the model exists.")

        # prevent name duplicates
        try:
            instances_with_same_name = ProgranServiceInstance.objects.get(name=self.name)

            if (not self.pk and instances_with_same_name) or (self.pk and self.pk != instances_with_same_name.pk):
                raise XOSValidationError("A ProgranServiceInstance with name '%s' already exists" % self.name)
        except self.DoesNotExist:
            pass

        if self.is_new and not self.created_by:
            # NOTE if created_by is null it has been created by XOS
            self.created_by = "XOS"


        # check that the sum of upload and download rate for a single enodeb is not greater than 95
        if not self.deleted:
            limit = 95
            same_enodeb = ProgranServiceInstance.objects.filter(enodeb_id=self.enodeb_id)

            total_up = self.UlAllocRBRate
            total_down = self.DlAllocRBRate

            for p in same_enodeb:
                if p.pk != self.pk:
                    total_up = total_up + p.UlAllocRBRate
                    total_down = total_down + p.DlAllocRBRate

            if total_up > limit:
                raise XOSValidationError("UlAllocRBRate for the enodeb associated with this profile is greater than %s" % limit)

            if total_down > limit:
                raise XOSValidationError("DlAllocRBRate for the enodeb associated with this profile is greater than %s" % limit)

        super(ProgranServiceInstance, self).save(*args, **kwargs)


