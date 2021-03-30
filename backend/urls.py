from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from graphene_django.views import GraphQLView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql", GraphQLView.as_view(graphiql=True)),
]


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
