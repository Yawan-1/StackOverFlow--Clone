from django.urls import path
from .views import index, about, category, work

urlpatterns = [
    path( '', index),
    path( 'about', about),
    path( 'category', category),
    path( 'work', work),
]
