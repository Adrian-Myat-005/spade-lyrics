from django.contrib import admin
from django import forms
from .models import Artist, Song, Annotation, SpadeSession

class SongAdminForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = '__all__'
        widgets = {
            'lyrics': forms.Textarea(attrs={'rows': 20, 'cols': 80, 'style': 'font-family: monospace; white-space: pre;'}),
        }

class AnnotationInline(admin.StackedInline):
    model = Annotation
    extra = 1

class SpadeSessionInline(admin.StackedInline):
    model = SpadeSession
    extra = 0

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    form = SongAdminForm
    list_display = ('title', 'artist', 'status', 'featured', 'is_spade_exclusive')
    list_filter = ('status', 'featured', 'is_spade_exclusive', 'artist')
    search_fields = ('title', 'lyrics', 'artist__name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [AnnotationInline, SpadeSessionInline]
    
    actions = ['make_published']

    @admin.action(description='Mark selected songs as Published')
    def make_published(self, request, queryset):
        queryset.update(status='published')

    class Media:
        js = ('admin/js/song_admin.js',)

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('song', 'lyric_snippet', 'created_by')
    search_fields = ('song__title', 'lyric_snippet', 'explanation')

@admin.register(SpadeSession)
class SpadeSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'song', 'session_type', 'published_at')
    list_filter = ('session_type',)