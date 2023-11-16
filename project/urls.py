from django.contrib import admin
from django.urls import include
from django.urls import path

urlpatterns = [
    path("", include("app_main.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/", include("app_api_v1.urls")),
    path("api/v2/", include("app_api_v2.urls")),
]
