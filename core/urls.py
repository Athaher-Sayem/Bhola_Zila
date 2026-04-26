from django.urls import path
from . import views
app_name = 'core'
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('hero/upload/', views.hero_upload, name='hero_upload'),
    path('hero/<uuid:pk>/delete/', views.hero_delete, name='hero_delete'),
]