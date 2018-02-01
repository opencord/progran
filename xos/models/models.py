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

        super(ENodeB, self).save(*args, **kwargs)


class Handover(Handover_decl):
    class Meta:
        proxy = True


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

        # TODO when saving set status to "in progress"
        super(ProgranServiceInstance, self).save(*args, **kwargs)


