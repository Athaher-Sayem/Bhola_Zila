from django.urls import path
from . import views
app_name = 'feedback'
urlpatterns = [
    path('',                views.submit_feedback, name='submit'),
    path('thanks/',         views.thanks,          name='thanks'),
    path('manage/',         views.feedback_list,   name='list'),
    path('manage/<uuid:pk>/', views.feedback_detail, name='detail'),
]