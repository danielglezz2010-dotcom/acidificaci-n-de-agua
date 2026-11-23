from django.contrib import admin

from .models import RegistroAcidificacion


@admin.register(RegistroAcidificacion)
class RegistroAcidificacionAdmin(admin.ModelAdmin):
    list_display = (
        "equipo", "fecha_registro",
        "ph_1", "ph_2", "ph_3", "ph_4",
        "resultado_1", "resultado_2", "resultado_3", "resultado_4",
        "acidez_critica",
    )
    list_filter = ("fecha_registro",)
    search_fields = ("equipo",)
    readonly_fields = ("fecha_registro", "resultado_1", "resultado_2", "resultado_3", "resultado_4")

    @admin.display(boolean=True, description="Acidez crítica")
    def acidez_critica(self, obj):
        return obj.tiene_acidez_critica()
