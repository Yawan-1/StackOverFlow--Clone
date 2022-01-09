"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from qa import views as qa_views
# import debug_toolbar
# Done
handler404 = qa_views.handler404
handler500 = qa_views.handler500

urlpatterns = [
    path('adminisGoodofmy_clone_so/', admin.site.urls),
    path('', include('profile.urls')),
    path('', include('qa.urls')),
    path('', include('notification.urls')),
    path('', include('tagbadge.urls')),
    path('', include('help.urls')),
    path('', include('review.urls')),
    path('', include('tools.urls')),
    path('accounts/',include('users.urls')),
    path('adminactions/', include('adminactions.urls')),
    path('martor/', include('martor.urls')),
    # path('__debug__/', include(debug_toolbar.urls)),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
