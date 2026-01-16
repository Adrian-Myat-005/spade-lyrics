from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Song, Artist, Genre, Producer
import json

def index(request):
    # --- ARCHIVE SEARCH & FILTER LOGIC ---
    query = request.GET.get('q', '')
    genre_slug = request.GET.get('genre', '')
    sort_by = request.GET.get('sort', 'newest') # newest, views, bpm, title
    
    songs = Song.objects.filter(status='published').select_related('artist').prefetch_related('genres', 'producers')

    # 1. Search Filter
    if query:
        songs = songs.filter(
            Q(title__icontains=query) |
            Q(artist__name__icontains=query) |
            Q(producers__name__icontains=query)
        ).distinct()

    # 2. Genre Filter
    if genre_slug:
        songs = songs.filter(genres__slug=genre_slug)

    # 3. Sorting
    if sort_by == 'views':
        songs = songs.order_by('-views')
    elif sort_by == 'bpm':
        songs = songs.order_by('bpm') # Slow to fast
    elif sort_by == 'title':
        songs = songs.order_by('title')
    else: # newest
        songs = songs.order_by('-release_date', '-id')

    # Context Data
    genres = Genre.objects.all().order_by('name')
    trending_songs = Song.objects.filter(status='published', is_trending=True).order_by('-views')[:5]

    context = {
        'archive_list': songs,
        'genres': genres,
        'trending_songs': trending_songs,
        'current_sort': sort_by,
        'current_genre': genre_slug,
        'query': query,
    }
    return render(request, 'home.html', context)

def song_detail(request, slug):
    song = get_object_or_404(Song, slug=slug)
    
    # Increment View Count
    song.views += 1
    song.save(update_fields=['views'])
    
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