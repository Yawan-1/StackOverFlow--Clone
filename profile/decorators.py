from django.shortcuts import redirect
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from qa.models import BannedUser

def unBanRequired(function):

	def keepUserOut(request, *args, **kwargs):
		if request.user.is_authenticated:
			if BannedUser.objects.filter(user=request.user, is_banned=False).exists():
				return redirect('profile:home')
			else:
				return function(request, *args, **kwargs)

		else:
			return redirect('users:login_request')

	return keepUserOut

def profileOwnerRequired_For_Edit(function):

	def keepUnknownUser_Out(request, *args, **kwargs):
		if request.user.is_authenticated:
			if request.user == request.user.profile.user:
				return function(request, *args, **kwargs)
			else:
				messages.error(request, 'Not Authorised')

		else:
			return redirect('users:login_request')

	return keepUnknownUser_Out

