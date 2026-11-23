# Estudio y Monitoreo de la Acidificación del Agua

App web en Django (MVT) para registrar 4 mediciones de pH por equipo, calcular el
índice de acidez automáticamente y graficarlo con Chart.js.

**Fórmula:** `Índice de acidez = 10^(7 − pH)` (veces más ácida que el agua neutra, pH 7).
**Acidez crítica:** cualquier medición con pH < 6.5 (`UMBRAL_PH_CRITICO` en `laboratorio/models.py`).

## Puesta en marcha (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations laboratorio
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Sitio: http://127.0.0.1:8000/  ·  Admin: http://127.0.0.1:8000/admin/
- Pruebas: `python manage.py test`

Consultar registros es público; crear, editar y eliminar requiere iniciar sesión.
