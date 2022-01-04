from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'tagbadge'

urlpatterns = [

	path('badges/', views.badges, name='badges'),

	path('taggedItems/<int:tag_id>/<int:user_id>/', views.taggedItems, name='taggedItems'),

	path('taggedItemsFrom_All/<int:tag_id>/', views.taggedItemsFrom_All, name='taggedItemsFrom_All'),

]