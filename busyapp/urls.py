from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('onthego/', views.onthego, name='onthego'),
    path('theplanner/', views.theplanner, name='theplanner'),
    path('tourist/', views.tourist, name='tourist'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('accessibility/', views.accessibility, name='accessibility'),
    path('test/', views.testView, name='testView'),
    path('onthego/formdata', views.onthegoform, name="onthegoform"),
    path('planner/formdata', views.plannerform, name="plannerform"),
    path('tourist/formdata', views.touristform, name="onthegoform"),
    path('accessibility/formdata', views.theplanner, name="accessibilityform"),
    path('busstops', views.busStops, name="busstops"),
    path('autocomp', views.busStopAutosuggest, name="autocomp_stops"),
    path('autocomp/routes', views.busRoutesAutosuggest, name="autocomp_routes"),
    path('loaderio-e39f002a9fff5739d5e13b22d4f09b69.txt', views.loadTest, name="loaderio"),
    path('directions', views.directions, name="directions"),
]