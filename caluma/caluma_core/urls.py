from django.conf import settings
from django.urls import re_path

from caluma.caluma_core import views as core_views
from caluma.caluma_form import views as form_views
from caluma.caluma_user.views import AuthenticationGraphQLView

urlpatterns = [
    re_path(
        "graphql/?",
        AuthenticationGraphQLView.as_view(graphiql=settings.DEBUG),
        name="graphql",
    ),
    re_path("healthz/?", core_views.health_check_status, name="healthz"),
    re_path("minio-callback/?", form_views.minio_callback_view, name="minio-callback"),
]
