from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Include admin URLs
    #ath('admin/adminaccount/', views.adminaccount, name='adminaccount'),
    # Your existing URLs
    #path('adminaccount/', views.myaccount, name='adminaccount'),
    path('', views.home, name='home'),
    path('myaccount/', views.myaccount, name='myaccount'),
    path('report/', views.report, name='report'),
    # path('upload/', views.upload, name='upload'),
    path('viewuploads/', views.viewuploads, name='viewuploads'),
    path('viewreport/<int:report_id>/', views.view_report, name='view_report'),
    # path('accounts/', include('allauth.urls')),  # resetting everything
    # path('accounts/google/login/', views.redirect_to_google_login, name='google_login'),
    path('accounts/login/', views.custom_login, name='custom_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('signup/', views.custom_signup, name='signup'),
    path('redirect-to-google/', views.redirectToGoogle, name='redirect_to_google'),
    # path('custom_login/', views.custom_login, name='custom_login'),
]
