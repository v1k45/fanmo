from django.http.response import HttpResponse
from django.utils import timezone
from import_export import resources
from import_export.formats.base_formats import CSV

from memberships.payments.models import Payment


class ModelResource(resources.ModelResource):
    def export_csv(self, queryset):
        export_formatter = CSV()
        export_file = export_formatter.export_data(self.export(queryset))
        file_name = f"{queryset.model._meta.model_name}-{timezone.now().isoformat()}.{export_formatter.get_extension()}"

        response = HttpResponse(
            export_file, content_type=export_formatter.get_content_type()
        )
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response
