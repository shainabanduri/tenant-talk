from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'admin'

urlpatterns = [
    path('', views.adminhome, name='adminhome'),  # Root URL without a trailing slash
    path('myaccount/', views.adminaccount, name='adminaccount'),
]
