from django.urls import path
from . import views
app_name = 'events'
urlpatterns = [
    path('', views.event_list, name='list'),
    path('create/', views.event_create, name='create'),
    path('<uuid:pk>/', views.event_detail, name='detail'),
    path('<uuid:pk>/delete/', views.event_delete, name='delete'),
    path('<uuid:pk>/register/', views.event_register, name='register'),
    path('<uuid:pk>/unregister/', views.event_unregister, name='unregister'),
    path('<uuid:pk>/registrations/', views.event_registrations, name='registrations'),
]
