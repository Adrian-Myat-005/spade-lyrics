from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Song, Artist

def song_detail(request, slug):
    song = get_object_or_404(Song, slug=slug)
    
    # Get the primary video (Spade Session) or fallback
    # We prefer a Spade Session if it exists
    main_video = song.spade_sessions.first()
    
    # Get all annotations for this song
    annotations = song.annotations.all()
    
    # Create a dictionary for easy lookup in the template/JS
    # Key: lyric_snippet (stripped of brackets if necessary, but here likely exact match)
    # Value: explanation
    annotations_dict = {a.lyric_snippet: a.explanation for a in annotations}
    
    return render(request, 'music/song_detail.html', {
        'song': song,
        'annotations_json': annotations_dict,
        'main_video': main_video,
    })

def search_results(request):
    query = request.GET.get('q', '')
    songs = []
    artists = []
    
    if query:
        # icontains handles case-insensitive matching and usually works well with Unicode
        songs = Song.objects.filter(
            Q(title__icontains=query) | Q(lyrics__icontains=query)
        ).distinct()[:5]
        
        artists = Artist.objects.filter(
            name__icontains=query
        )[:3]
    
    return render(request, 'music/partials/search_results.html', {
        'songs': songs,
        'artists': artists,
        'query': query,
    })
