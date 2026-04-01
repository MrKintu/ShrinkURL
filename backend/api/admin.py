from django.contrib import admin
from .models import URLMapping

# Extend User admin to include profile
admin.site.register(URLMapping)
