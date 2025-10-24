from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),  # Ruta para el panel de administración
    path('', RedirectView.as_view(url='/login/', permanent=False)),  # Redirige la raíz a /login/
    path('login/', include('ong_app.urls')),  # Incluye las URLs de ong_app
]