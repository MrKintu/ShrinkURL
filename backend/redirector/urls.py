from django.urls import path
from . import views

urlpatterns = [
    path('<str:short_code>/', views.redirect_to_original, name='redirect_to_original'),
]
