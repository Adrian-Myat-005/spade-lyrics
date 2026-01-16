from django.db import models
from django.contrib.auth.models import User

class Artist(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    bio = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='artists/', blank=True, null=True)
    facebook_link = models.URLField(blank=True)
    instagram_link = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Producer(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs')
    producers = models.ManyToManyField(Producer, related_name='songs', blank=True)
    genres = models.ManyToManyField(Genre, related_name='songs', blank=True)
    
    # Metadata for Database Feel
    bpm = models.IntegerField(null=True, blank=True, help_text="Beats Per Minute")
    key = models.CharField(max_length=10, null=True, blank=True, help_text="e.g. C# Minor")
    views = models.PositiveIntegerField(default=0)
    
    lyrics = models.TextField(help_text="Enter lyrics here. Annotations will be linked to text segments.")
    album = models.CharField(max_length=200, blank=True)
    release_date = models.DateField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, help_text="Full YouTube video URL")
    featured = models.BooleanField(default=False)
    is_spade_exclusive = models.BooleanField(default=False, help_text="Mark if this content is produced by Spade.")
    is_trending = models.BooleanField(default=False, help_text="Check this to show in the Trending section.")
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    def get_rendered_lyrics(self):
        """
        Parses the lyrics field.
        Replaces text inside brackets like [Lyric] with:
        <span class="cursor-pointer border-b-2 border-spade-red hover:bg-spade-dark-red/30 transition-colors"
              @click.stop="openAnnotation('Lyric')">Lyric</span>
        """
        import re

        def replace_match(match):
            # content inside brackets
            text = match.group(1)
            # Escape quotes in text if necessary, though simpler is safer
            return f'<span class="cursor-pointer border-b border-red-600 hover:bg-red-900/50 transition-colors" @click.stop="openAnnotation(\'{text}\')" :class="activeAnnotation?.snippet === \'{text}\' ? \'bg-red-600 text-black font-bold\' : \'\'">{text}</span>'

        # Regex to find [text]
        # Non-greedy match for content inside brackets
        rendered = re.sub(r'\[(.*?)\]', replace_match, self.lyrics)
        return rendered

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

class Annotation(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='annotations')
    lyric_snippet = models.CharField(max_length=255, help_text="The specific text segment being annotated.")
    explanation = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Annotation for {self.song.title}: {self.lyric_snippet[:30]}..."

class SpadeSession(models.Model):
    SESSION_TYPES = [
        ('dig', 'The Dig (Interview)'),
        ('uncover', 'Uncover (Lyrics Breakdown)'),
        ('performance', 'Live Performance'),
    ]

    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='spade_sessions', null=True, blank=True)
    title = models.CharField(max_length=200)
    youtube_id = models.CharField(max_length=50, help_text="The 11-character YouTube Video ID")
    session_type = models.CharField(max_length=50, choices=SESSION_TYPES, default='uncover')
    description = models.TextField(blank=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_session_type_display()}: {self.title}"
