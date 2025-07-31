from django.contrib import admin
from django.urls import include, path
from django_extended.swagger_view import schema_view

api = [
    path("users/", include("users.urls")),
    path("wallets/", include("wallets.urls")),
]

urlpatterns = [
    path("api/", include(api)),
    path("admin/", admin.site.urls),
]

urlpatterns += [
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
