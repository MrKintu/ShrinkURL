"""
URL configuration for shrinkURL project.

Routes:
    - /admin/ - Django admin interface
    - /api/   - API endpoints for URL shortening
    - /<short_code>/ - Redirector for short URLs
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path('api/', include('api.urls')),
    path('', include('redirector.urls')),  # Root level for short codes
]
