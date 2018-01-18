from core.models import Service
from xos.exceptions import XOSValidationError

from models_decl import ProgranService_decl
from models_decl import ENodeB_decl
from models_decl import Handover_decl
from models_decl import ProgranServiceInstance_decl







class ProgranService(ProgranService_decl):
    class Meta:
        proxy = True


class ENodeB(ENodeB_decl):
    class Meta:
        proxy = True


class Handover(Handover_decl):
    class Meta:
        proxy = True


class ProgranServiceInstance(ProgranServiceInstance_decl):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        # NOTE someone is setting owner_id, so just override it for now
        # if not self.owner_id:
        services = Service.objects.all()
        services = [s for s in services if s.name.lower() == 'progran']

        # NOTE select the correct owner
        try:
            progran_service = services[0]
            self.owner_id = progran_service.id
        except IndexError:
            raise XOSValidationError("Service Progran cannot be found, please make sure that the model exists.")

        # NOTE if the instance is new, check that the name is not duplicated
        instances_with_same_name = None
        if self.pk is None:
            try:
                instances_with_same_name = ProgranServiceInstance.objects.get(name=self.name)
            except self.DoesNotExist:
                # it's ok not to find anything here
                pass

        if instances_with_same_name:
            raise XOSValidationError("A ProgranServiceInstance with name '%s' already exists" % self.name)
        super(ProgranServiceInstance, self).save(*args, **kwargs)


