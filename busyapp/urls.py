from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('onthego/', views.onthego, name='onthego'),
    path('theplanner/', views.theplanner, name='theplanner'),
    path('tourist/', views.tourist, name='tourist'),
    path('test/', views.testView, name='testView'),
    path('onthego/formdata', views.onthegoform, name="onthegoform"),
    path('planner/formdata', views.plannerform, name="onthegoform"),
    path('tourist/formdata', views.touristform, name="onthegoform"),
]