from django.conf.urls import include, url
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    url(r"^api-token-auth/", obtain_jwt_token),
    url(r"^api-token-refresh/", refresh_jwt_token),
    url(r"^api/v1/", include("caluma.form.urls")),
]
