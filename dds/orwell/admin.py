# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from models import Slide, Client, ClientActivity, ClientToGroup, Location, Playlist, PlaylistItemSlide, PlaylistItemGroup, Template
from django.contrib import admin

class SlideAdmin(admin.ModelAdmin):
    exclude = ['last_update']
    list_display = ('title', 'user', 'group', 'expires_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'group')
        }),
        (None, {
            'fields': ('priority', 'duration', 'expires_at', 'thumbnail',
                       'bundle'),
        }),
    )

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk', 'playlist', 'location', 'last_contact')

class PlaylistItemSlideInline(admin.TabularInline):
    model = PlaylistItemSlide
    extra = 2

class PlaylistItemGroupInline(admin.TabularInline):
    model = PlaylistItemGroup
    extra = 2

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [
        PlaylistItemSlideInline,
        PlaylistItemGroupInline,
    ]

admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Slide, SlideAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Location)
admin.site.register(ClientActivity)
admin.site.register(Template)
