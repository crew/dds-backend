# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from models import Slide, Client, ClientActivity, Location, Playlist, PlaylistItem, Template, TemplateSlide
from django.contrib import admin

class SlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'expires_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'user')
        }),
        (None, {
            'fields': ('priority', 'expires_at', 'thumbnail',
                       'bundle'),
        }),
    )

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk', 'playlist', 'location', 'last_contact')

class PlaylistItemInline(admin.TabularInline):
    model = PlaylistItem
    extra = 2

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [PlaylistItemInline]

admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(Slide, SlideAdmin)
admin.site.register(TemplateSlide)
admin.site.register(Client, ClientAdmin)
admin.site.register(Location)
admin.site.register(ClientActivity)
admin.site.register(Template)
