from django.urls import path
from . import views
app_name = 'notices'
urlpatterns = [
    path('', views.notice_list, name='list'),
    path('create/', views.notice_create, name='create'),
    path('<uuid:pk>/delete/', views.notice_delete, name='delete'),
]
