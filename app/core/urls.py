from django.urls import include, path
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from rest_framework import routers

from core import views

router = routers.DefaultRouter()
router.register(r"checks", views.CheckViewSet)
router.register(r"printers", views.PrinterViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            template_name="swagger-ui.html",
            url_name="schema",
        ),
        name="swagger-ui",
    ),
]
