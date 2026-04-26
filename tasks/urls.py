from django.urls import path
from . import views
app_name = 'tasks'
urlpatterns = [
    path('',                    views.task_list,   name='list'),
    path('create/',             views.task_create, name='create'),
    path('<uuid:pk>/',          views.task_detail, name='detail'),
    path('<uuid:pk>/update/',   views.task_update_status, name='update_status'),
    path('<uuid:pk>/delete/',   views.task_delete, name='delete'),
]