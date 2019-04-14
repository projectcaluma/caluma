from django.conf import settings
from django.conf.urls import include, url
from graphene_django.views import GraphQLView

urlpatterns = [
    url(r"^graphql", GraphQLView.as_view(graphiql=settings.DEBUG), name="graphql")
]

urlpatterns += [url(r"^silk/", include("silk.urls", namespace="silk"))]
