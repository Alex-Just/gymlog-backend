import uuid_utils as uuid
from django.contrib import admin
from django.db.models import Model
from django.db.models import UUIDField


def generate_uuid7():
    # Simple `uuid.uuid7` throws an error:
    # “0190db2d-984c-7132-999f-c14433f25068” is not a valid UUID.
    return str(uuid.uuid7())


class UUIDModel(Model):
    id = UUIDField(primary_key=True, default=generate_uuid7, editable=False)

    class Meta:
        abstract = True


class GeneralModelAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        return [*list(fields), "created", "modified"]

    def lookup_allowed(self, *args, **kwargs):
        return True

    def get_list_display_links(self, request, list_display):
        return self.get_list_display(request)
