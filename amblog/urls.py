"""amblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('__site-admin__/', admin.site.urls),
    # Include Python-Social-Auth URLs
    path('social/', include('social_django.urls', namespace='social')),
    # Include blog app URLs
    path('', include('blog.urls', namespace='blog')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('privacy-policy/', TemplateView.as_view(template_name='privacy_policy.html'),
         name='privacy-policy'),
    path('cookie-policy/', TemplateView.as_view(template_name='cookie_policy.html'),
         name='cookie-policy'),
    path('disclaimer/', TemplateView.as_view(template_name='disclaimer.html'),
         name='disclaimer'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve static files during dev
