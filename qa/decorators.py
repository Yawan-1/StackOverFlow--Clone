from django.shortcuts import redirect,render
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied

def loggedOutFromAllDevices(function):
	def logOutFunc(request, *args, **kwargs):
		if request.user.is_authenticated:
			if request.user.profile.logout_on_all_devices == False:
				return function(request, *args, **kwargs)
			else:
				logout(request)
				return redirect("profile:home")

		else:
			return redirect('users:login_request')

	return logOutFunc

def superuser_only(function):

	def _inner(request, *args, **kwargs):
		if not request.user.is_superuser:
			raise PermissionDenied           
		return function(request, *args, **kwargs)
	return _inner

def highModRequired(function):

	def keepNormalOut(request, *args, **kwargs):
		if request.user.is_authenticated:
			if request.user.profile.is_high_moderator:
				return function(request, *args, **kwargs)
			else:
				return render(request, 'Denied/HighModRequired.html')

		else:
			return redirect('users:login_request')

	return keepNormalOut


def access_mod_tools_priv_required(function):

	def keepNormalOut(request, *args, **kwargs):
		if request.user.is_authenticated:
			if request.user.profile.accessTo_moderatorTools:
				return function(request, *args, **kwargs)
			else:
				return render(request, 'Denied/requiredRep_1000.html')

		else:
			return redirect('users:login_request')

	return keepNormalOut
