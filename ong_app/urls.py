# ong_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar_alumno/', views.registrar_alumno, name='registrar_alumno'),
    path('registrar_usuarios/', views.registrar_usuarios, name='registrar_usuarios'),
    path('inicio_maestro/', views.inicio_maestro, name='inicio_maestro'),
    path('inicio_maestro/', views.inicio_psicologo, name='inicio_maestro'),
    path('registrar_alumno_maestro/', views.registrar_alumno_maestro, name='registrar_alumno_maestro'),
    path('alumno/<int:id_alumno>/', views.ver_alumno, name='ver_alumno'),
    path('alumno/eliminar/<int:id_alumno>/', views.eliminar_alumno, name='eliminar_alumno'),
    path('alumno/<int:id_alumno>/agregar_nota/', views.agregar_nota, name='agregar_nota'),
    path('alumno/<int:alumno_id>/agregar_actividad/', views.agregar_actividad, name='agregar_actividad'),
    path('actividades/lista/', views.lista_actividades, name='lista_actividades'),
    path('actividades/editar/<int:id_actividad>/', views.editar_actividad, name='editar_actividad'),
     path('actividades/eliminar/<int:id_actividad>/', views.eliminar_actividad, name='eliminar_actividad'),
]
