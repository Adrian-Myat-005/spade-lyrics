from django.contrib import admin
from django import forms
from .models import Artist, Song, Annotation, SpadeSession

# 1. Custom Form (Keeps your nice styling for the lyrics box)
class SongAdminForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = '__all__'
        widgets = {
            'lyrics': forms.Textarea(attrs={
                'rows': 20,
                'cols': 80,
                'style': 'font-family: monospace; white-space: pre; background-color: #f8f8f8;'
            }),
        }

# 2. Inlines (This puts Annotations INSIDE the Song page)
class AnnotationInline(admin.TabularInline): # Changed to Tabular for cleaner layout
    model = Annotation
    extra = 1
    fields = ['lyric_snippet', 'explanation']
    classes = ['collapse'] # Allows you to hide/show them to save space

class SpadeSessionInline(admin.StackedInline):
    model = SpadeSession
    extra = 0
    classes = ['collapse']

# 3. Artist Admin
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# 4. Song Admin (The Main Dashboard)
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    form = SongAdminForm

    # Updated to include 'is_trending' and annotation count
    list_display = ('title', 'artist', 'status', 'is_trending', 'featured', 'view_annotation_count')

    # Filters on the right sidebar
    list_filter = ('status', 'is_trending', 'featured', 'is_spade_exclusive', 'artist')

    # Search bar config
    search_fields = ('title', 'lyrics', 'artist__name')

    # Auto-fill the slug when you type the title
    prepopulated_fields = {'slug': ('title',)}

    # The magic part: Show Annotations and Sessions directly on the Song page
    inlines = [AnnotationInline, SpadeSessionInline]

    actions = ['make_published', 'make_trending']

    # Custom Actions
    @admin.action(description='Mark selected songs as Published')
    def make_published(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description='Mark selected songs as Trending')
    def make_trending(self, request, queryset):
        queryset.update(is_trending=True)

    # Custom Column to count annotations
    def view_annotation_count(self, obj):
        count = obj.annotations.count()
        return f"{count} annotations"
    view_annotation_count.short_description = 'Annotations'

    # Note: I removed the 'Media' class linking to 'song_admin.js'
    # unless you have actually created that file, otherwise it causes 404 errors.

# 5. Other Admins (Optional, if you want to see them separately)
@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('song', 'lyric_snippet', 'created_by')
    search_fields = ('song__title', 'lyric_snippet', 'explanation')
    autocomplete_fields = ['song'] # Useful if you have many songs

@admin.register(SpadeSession)
class SpadeSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'song', 'session_type', 'published_at')
    list_filter = ('session_type',)