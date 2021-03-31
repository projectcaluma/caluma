from django.conf import settings
from django.urls import re_path

from caluma.caluma_core import views
from caluma.caluma_user.views import AuthenticationGraphQLView

urlpatterns = [
    re_path(
        "graphql/?",
        AuthenticationGraphQLView.as_view(graphiql=settings.DEBUG),
        name="graphql",
    ),
    re_path("healthz/?", views.health_check_status, name="healthz"),
]
