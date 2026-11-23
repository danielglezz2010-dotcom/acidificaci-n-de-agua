from django.urls import path

from . import views

urlpatterns = [
    path("", views.RegistroListView.as_view(), name="registro_list"),
    path("registro/nuevo/", views.RegistroCreateView.as_view(), name="registro_create"),
    path("registro/<int:pk>/", views.RegistroDetailView.as_view(), name="registro_detail"),
    path("registro/<int:pk>/editar/", views.RegistroUpdateView.as_view(), name="registro_update"),
    path("registro/<int:pk>/eliminar/", views.RegistroDeleteView.as_view(), name="registro_delete"),
]
