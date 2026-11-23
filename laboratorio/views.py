from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import RegistroForm
from .models import UMBRAL_PH_CRITICO, RegistroAcidificacion


def _parse_fecha(texto):
    """Acepta AAAA-MM-DD o DD/MM/AAAA. Devuelve una fecha o None."""
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


# ---------- Consulta pública ----------
class RegistroListView(ListView):
    model = RegistroAcidificacion
    template_name = "laboratorio/registro_list.html"
    context_object_name = "registros"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q:
            filtro = Q(equipo__icontains=q)
            fecha = _parse_fecha(q)
            if fecha:
                filtro |= Q(fecha_registro__date=fecha)
            queryset = queryset.filter(filtro)
        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["q"] = self.request.GET.get("q", "").strip()
        return contexto


class RegistroDetailView(DetailView):
    model = RegistroAcidificacion
    template_name = "laboratorio/registro_detail.html"
    context_object_name = "registro"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        registro = self.object
        # Datos para Chart.js (se inyectan con json_script en la plantilla)
        contexto["chart_data"] = {
            "labels": [f"Medida {fila['n']}" for fila in registro.filas],
            "ph": registro.mediciones,
            "resultados": registro.resultados,
        }
        contexto["umbral"] = UMBRAL_PH_CRITICO
        return contexto


# ---------- Escritura (requiere login) ----------
class RegistroGuardarMixin(LoginRequiredMixin, SuccessMessageMixin):
    """Comportamiento común de crear y editar: login + mensajes flash + alerta crítica."""

    model = RegistroAcidificacion
    form_class = RegistroForm
    template_name = "laboratorio/registro_form.html"

    def form_valid(self, form):
        respuesta = super().form_valid(form)  # guarda (calcula resultados) y añade el mensaje de éxito
        if self.object.tiene_acidez_critica():
            messages.error(
                self.request,
                f"¡Acidez crítica! Al menos una medición tiene pH menor a {UMBRAL_PH_CRITICO}.",
            )
        return respuesta


class RegistroCreateView(RegistroGuardarMixin, CreateView):
    success_message = "Registro del equipo «%(equipo)s» creado correctamente."


class RegistroUpdateView(RegistroGuardarMixin, UpdateView):
    success_message = "Registro del equipo «%(equipo)s» actualizado correctamente."


class RegistroDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = RegistroAcidificacion
    template_name = "laboratorio/registro_confirm_delete.html"
    context_object_name = "registro"
    success_url = reverse_lazy("registro_list")
    success_message = "El registro fue eliminado."
