from django.shortcuts import render
from .models import PrivRepNotification,Notification
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse


def read_All_Notifications(request):

    notifics = Notification.objects.filter(noti_receiver=request.user).order_by('-date_created')

    for objs in notifics:
        objs.is_read = True
        objs.save()

    # return HttpResponse(status=204)
    return JsonResponse({'action': 'readedAll'})

def read_All_Priv_Notifications(request):

    notifications = PrivRepNotification.objects.filter(for_user=request.user)

    for obj in notifications:
        obj.is_read = True
        obj.save()

    return JsonResponse({'action':'readedAllPrivNotifications'})

