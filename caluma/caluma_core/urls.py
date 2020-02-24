from django.conf import settings
from django.conf.urls import url

from caluma.caluma_user.views import AuthenticationGraphQLView

urlpatterns = [
    url(r"", AuthenticationGraphQLView.as_view(graphiql=settings.DEBUG), name="graphql")
]
