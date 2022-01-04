from django.contrib import admin

from .models import Notification,PrivRepNotification

admin.site.register(Notification)

admin.site.register(PrivRepNotification)
