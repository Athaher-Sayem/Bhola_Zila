from django.urls import path
from . import views
app_name = 'gallery'
urlpatterns = [
    path('', views.gallery_view, name='gallery'),
    path('upload/', views.gallery_upload, name='upload'),
    path('<uuid:pk>/delete/', views.gallery_delete, name='delete'),
]
