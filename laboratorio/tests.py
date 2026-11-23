from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import RegistroAcidificacion, calcular_indice_acidez


class FormulaTests(TestCase):
    def test_indice_acidez(self):
        self.assertAlmostEqual(calcular_indice_acidez(7), 1)
        self.assertAlmostEqual(calcular_indice_acidez(5), 100)
        self.assertAlmostEqual(calcular_indice_acidez(8), 0.1)


class VistasTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("alumno", password="clave12345")
        self.registro = RegistroAcidificacion.objects.create(
            equipo="Equipo A", ph_1=7, ph_2=6, ph_3=5, ph_4=4
        )

    def test_resultados_calculados_al_guardar(self):
        self.assertAlmostEqual(self.registro.resultado_1, 1)
        self.assertAlmostEqual(self.registro.resultado_3, 100)

    def test_acidez_critica(self):
        self.assertTrue(self.registro.tiene_acidez_critica())

    def test_lista_y_detalle_son_publicos(self):
        self.assertEqual(self.client.get(reverse("registro_list")).status_code, 200)
        self.assertEqual(self.client.get(self.registro.get_absolute_url()).status_code, 200)

    def test_crear_requiere_login(self):
        respuesta = self.client.get(reverse("registro_create"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/accounts/login/", respuesta.url)

    def test_buscador(self):
        self.assertContains(self.client.get(reverse("registro_list"), {"q": "Equipo A"}), "Equipo A")
        self.assertNotContains(self.client.get(reverse("registro_list"), {"q": "zzz"}), "Equipo A")

    def test_crear_con_login_calcula_y_avisa(self):
        self.client.login(username="alumno", password="clave12345")
        datos = {"equipo": "Equipo B", "ph_1": 7, "ph_2": 7, "ph_3": 5, "ph_4": 7, "leyenda": ""}
        respuesta = self.client.post(reverse("registro_create"), datos, follow=True)
        self.assertEqual(respuesta.status_code, 200)
        nuevo = RegistroAcidificacion.objects.get(equipo="Equipo B")
        self.assertAlmostEqual(nuevo.resultado_3, 100)
        self.assertContains(respuesta, "Acidez crítica")
