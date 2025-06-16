"""
URL configuration for backendcomunity project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include, path #para importar las demas urls
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),      # <-- LOGIN JWT
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),     # <-- REFRESH JWT
     path('admin/', admin.site.urls),
     
    path('api/auth/', include('usuarios.urls')), 
    path('api/comunidad/', include('comunidad.urls')),
    path('api/reuniones/', include('reuniones.urls')),
    path('api/arriendos/', include('arriendos.urls')),
    path('api/finanzas/', include('finanzas.urls')),
    path('api/documentos/', include('documentos.urls')),
]

