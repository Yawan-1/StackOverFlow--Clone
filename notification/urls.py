from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [

	path('read_All_Notifications/', views.read_All_Notifications, name='read_All_Notifications'),

	path('read_All_Priv_Notifications/', views.read_All_Priv_Notifications, name='read_All_Priv_Notifications'),


]