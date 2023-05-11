from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

# DRF YASG
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="ChronoApp API",
        default_version="v1",
        description="",
        contact=openapi.Contact(
            name="Hanzla Tauqeer",
            url="https://www.linkedin.com/in/1hanzla100/",
            email="hanzla.tauqeer123@gmail.com",
        ),
        license=openapi.License(name="BSD License"),
    ),
    # public=False,
    permission_classes=(permissions.IsAdminUser,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/authentication/", include("authentication.urls")),
    path("api/watches/", include("watches.urls")),
    # Swagger
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]


if settings.DEBUG is not False:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
