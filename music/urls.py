from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from music import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('song/<slug:slug>/', views.song_detail, name='song_detail'),
    path('api/search/', views.search_suggestions, name='search_suggestions'),
]

# This part enables images to load:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)