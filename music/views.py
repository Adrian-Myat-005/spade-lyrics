from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Song, Artist
import json

def index(request):
    # 1. Trending Songs (Only those checked as 'is_trending')
    trending_songs = Song.objects.filter(status='published', is_trending=True).select_related('artist').order_by('-release_date')[:3]

    # 2. The Raw List (All published songs, newest first)
    all_uploads = Song.objects.filter(status='published').select_related('artist').order_by('-id')[:20]

    context = {
        'trending_songs': trending_songs,
        'all_uploads': all_uploads
    }
    return render(request, 'home.html', context)

def song_detail(request, slug):
    song = get_object_or_404(Song, slug=slug)
    rendered_lyrics = song.get_rendered_lyrics()
    annotations_list = list(song.annotations.values('lyric_snippet', 'explanation'))

    context = {
        'song': song,
        'rendered_lyrics': rendered_lyrics,
        'annotations_json': json.dumps(annotations_list),
    }
    return render(request, 'song_detail.html', context)

# NEW: Live Search Endpoint
def search_suggestions(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    # Search in Song Titles AND Artist Names
    songs = Song.objects.filter(
        Q(title__icontains=query) |
        Q(artist__name__icontains=query),
        status='published'
    )[:5] # Limit to 5 results

    results = []
    for song in songs:
        results.append({
            'title': song.title,
            'artist': song.artist.name,
            'url': f"/song/{song.slug}/",
            'type': 'Song'
        })

    return JsonResponse({'results': results})