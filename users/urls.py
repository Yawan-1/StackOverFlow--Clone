from django.urls import path,include

from . import views

app_name = 'users'

urlpatterns = [
	# path('',include('django.contrib.auth.urls')),
	
	path('signup_view/',views.signup_view, name='signup_view'),
	
	path('logout_view/', views.logout_view, name='logout_view'),
	
	path("login_request", views.login_request, name="login_request"),
	
	# path('login/', views.LoginView.as_view(), name='logins'),
]

