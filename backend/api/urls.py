from django.urls import path, include
from rest_framework import routers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import views


# Create router and register ViewSet
router = routers.DefaultRouter()
router.register(r'urls', views.URLMappingViewSet, basename='urlmapping')


@api_view(['GET'])
def api_root(request, format=None):
    """
    TinyScale API Root - URL Shortener API
    """
    return Response({
        'shorten': request.build_absolute_uri('shorten/'),
        'urls': request.build_absolute_uri('urls/'),
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('', include(router.urls)),
]
