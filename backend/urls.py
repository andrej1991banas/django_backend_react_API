"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Function for generating API documentation
schema_view = get_schema_view(
    openapi.Info(
        title='E-commerce Backend APIs',
        default_version="v1",
        description="This is the documentation for backend API",
        terms_of_service="http://www.example.com/terms/",
        contact=openapi.Contact(email="limitless.lokca@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ]
)

urlpatterns = [
    path("admin/", admin.site.urls),  # Corrected admin path
    path("api/v1/", include('api.urls')),  # Corrected API version 1 path

    # Documentation
    path("", schema_view.with_ui('swagger', cache_timeout=0), name="schema-swagger-ui"),
]



urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)