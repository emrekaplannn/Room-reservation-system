from django.contrib import admin
from django.urls import include, path
from room_reservation import views

urlpatterns = [
    path("room_reservation/", include("room_reservation.urls")),
    path("admin/", admin.site.urls),
    
    # path("", views.auth_form, name="auth_form"),
    # path('command_form/', views.command_form, name='command_form'),
    path('notifications/', views.notification_view, name='notification_view'),
    path('signin/', views.auth_view, name='authentication_view'),
    path('signup/', views.signup_view, name='signup_view'),
]