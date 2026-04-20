from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('team/', views.team_view, name='team'),
    path('verify-members/', views.verify_members, name='verify_members'),
    path('verify/<uuid:token>/', views.verify_email, name='verify_email'),
]
