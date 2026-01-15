from django.urls import path
from . import views

urlpatterns = [
    path('song/<slug:slug>/', views.song_detail, name='song_detail'),
    path('search/results/', views.search_results, name='search_results'),
]

