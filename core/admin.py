from django.contrib import admin
from django.utils import timezone

from .models import LicenciaMedica


@admin.register(LicenciaMedica)
class LicenciaMedicaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "funcionario",
        "rut_funcionario",
        "medico",
        "tipo_licencia_nombre",
        "dias_reposo",
        "estado",
        "fecha_emision",
        "eliminado",
    )
    list_filter = ("estado", "tipo_licencia", "eliminado", "fecha_emision")
    search_fields = (
        "medico",
        "rut_medico",
        "funcionario",
        "rut_funcionario",
        "motivo",
    )
    readonly_fields = ("fecha", "fecha_eliminacion")
    ordering = ("-fecha",)
    list_per_page = 25
    actions = ("soft_delete_selected",)

    @admin.display(description="Tipo de licencia", ordering="tipo_licencia")
    def tipo_licencia_nombre(self, obj):
        return obj.get_tipo_licencia_display()

    @admin.action(description="Marcar seleccionadas como eliminadas")
    def soft_delete_selected(self, request, queryset):
        fecha_eliminacion = timezone.now()
        actualizadas = queryset.filter(eliminado=False).update(
            eliminado=True,
            fecha_eliminacion=fecha_eliminacion,
        )
        self.message_user(
            request,
            f"{actualizadas} licencia(s) marcada(s) como eliminada(s).",
        )

    def delete_model(self, request, obj):
        obj.soft_delete()
