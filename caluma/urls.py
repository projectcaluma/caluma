from django.conf.urls import include, url

urlpatterns = [url(r"^graphql", include("caluma.caluma_core.urls"))]
