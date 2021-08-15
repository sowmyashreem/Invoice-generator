from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path( 'store', views.store),
    path('email_generator', views.email_generator),
]