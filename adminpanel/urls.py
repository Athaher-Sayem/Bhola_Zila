from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('',                                  views.dashboard,    name='dashboard'),
    path('users/',                              views.user_list,    name='users'),
    path('users/<uuid:pk>/action/',            views.user_action,  name='user_action'),
    path('content/',                            views.content_view, name='content'),
    path('content/event/<uuid:pk>/delete/',   views.delete_event, name='delete_event'),
    path('content/notice/<uuid:pk>/delete/',  views.delete_notice,name='delete_notice'),
    path('logs/',                               views.logs_view,          name='logs'),
    path('profile-changes/',                    views.profile_changes_view, name='profile_changes'),
]