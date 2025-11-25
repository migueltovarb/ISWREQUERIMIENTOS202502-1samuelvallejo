"""
URL configuration for crud_example project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect


def redirect_to_menu(request):
    if request.user.is_authenticated:
        return redirect('cafeteria:menu_principal')
    return redirect('login')


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home: si está logueado va al menú, si no al login
    path('', redirect_to_menu, name='home'),

    # Autenticación
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='login.html'),
        name='login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    # URLs de la app de la cafetería
    path('cafeteria/', include(('crud_example.proyecto_cafeteria.urls', 'cafeteria'), namespace='cafeteria')),
]

# Archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

