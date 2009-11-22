# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from models import Slide, Asset, Client, Location, ClientActivity
from django.contrib import admin


class AssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'url')


class SlideAdmin(admin.ModelAdmin):
    exclude = ['last_update']
    list_display = ('title', 'user', 'group', 'expires_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'group')
        }),
        (None, {
            'fields': ('priority', 'duration', 'expires_at', 'mode',
                       'transition'),
        }),
        ('Assets', {
            'fields': ('assets', 'thumbnail'),
        }),
    )


class ClientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'location', 'last_contact')


admin.site.register(Slide, SlideAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Location)
admin.site.register(ClientActivity)
