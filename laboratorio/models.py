from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

# Por debajo de este pH se considera "acidez crítica" (límite inferior del
# rango habitual de agua potable: 6.5 – 8.5). Ajústalo si tu docente indica otro.
UMBRAL_PH_CRITICO = 6.5


def calcular_indice_acidez(ph):
    """
    Fórmula elegida para el Resultado Final:

        Índice de acidez = 10 ** (7 - pH)

    Indica cuántas veces más ácida (o más básica) es la muestra respecto al
    agua neutra (pH 7). Ejemplos: pH 7 -> 1, pH 6 -> 10, pH 5 -> 100, pH 8 -> 0.1
    (porque el pH es una escala logarítmica de la concentración de H+).
    """
    return 10 ** (7 - ph)


class RegistroAcidificacion(models.Model):
    equipo = models.CharField("Equipo de laboratorio", max_length=100)
    fecha_registro = models.DateTimeField("Fecha y hora de registro", auto_now_add=True)

    _validadores_ph = [MinValueValidator(0), MaxValueValidator(14)]
    ph_1 = models.FloatField("Medida 1 (pH)", validators=_validadores_ph)
    ph_2 = models.FloatField("Medida 2 (pH)", validators=_validadores_ph)
    ph_3 = models.FloatField("Medida 3 (pH)", validators=_validadores_ph)
    ph_4 = models.FloatField("Medida 4 (pH)", validators=_validadores_ph)

    # Se calculan automáticamente en save(); no se capturan a mano.
    resultado_1 = models.FloatField("Resultado medida 1", editable=False, default=0)
    resultado_2 = models.FloatField("Resultado medida 2", editable=False, default=0)
    resultado_3 = models.FloatField("Resultado medida 3", editable=False, default=0)
    resultado_4 = models.FloatField("Resultado medida 4", editable=False, default=0)

    leyenda = models.TextField(
        "Leyenda de la gráfica",
        blank=True,
        help_text="Describe los ejes, colores y la tendencia que observas en la gráfica.",
    )

    class Meta:
        ordering = ["-fecha_registro"]
        verbose_name = "registro de acidificación"
        verbose_name_plural = "registros de acidificación"

    def __str__(self):
        return f"{self.equipo} – {self.fecha_registro:%d/%m/%Y %H:%M}" if self.fecha_registro else self.equipo

    def get_absolute_url(self):
        return reverse("registro_detail", args=[self.pk])

    # ---- Lógica de cálculo ----
    @property
    def mediciones(self):
        return [self.ph_1, self.ph_2, self.ph_3, self.ph_4]

    @property
    def resultados(self):
        return [self.resultado_1, self.resultado_2, self.resultado_3, self.resultado_4]

    def calcular_resultados(self):
        self.resultado_1, self.resultado_2, self.resultado_3, self.resultado_4 = (
            calcular_indice_acidez(ph) for ph in self.mediciones
        )

    def save(self, *args, **kwargs):
        # El cálculo ocurre siempre antes de guardar (formulario web o panel admin).
        self.calcular_resultados()
        super().save(*args, **kwargs)

    # ---- Ayudas para plantillas ----
    def tiene_acidez_critica(self):
        return any(ph < UMBRAL_PH_CRITICO for ph in self.mediciones)

    @property
    def filas(self):
        return [
            {"n": i, "ph": ph, "resultado": res, "critico": ph < UMBRAL_PH_CRITICO}
            for i, (ph, res) in enumerate(zip(self.mediciones, self.resultados), start=1)
        ]

    @property
    def leyenda_mostrada(self):
        if self.leyenda.strip():
            return self.leyenda
        return (
            "El eje izquierdo (azul) muestra el pH medido en cada toma; el eje derecho "
            "(rojo, escala logarítmica) muestra el índice de acidez 10^(7 − pH). "
            "Mientras más baja la línea azul, más alta la roja: a menor pH, mayor acidez."
        )
