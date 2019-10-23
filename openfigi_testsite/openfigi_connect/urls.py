from django.urls import path

from . import views

app_name='openfigi_connect'
urlpatterns = [
    path('', views.home_view, name='home')
]