from models import Slide, Asset, Client, Location
from django.contrib import admin


class AssetAdmin(admin.ModelAdmin):
#    fieldsets = [
#        (None, {'fields' : ['file']}),
#    ]
    list_display = ('id', 'file')


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
            'fields': ('assets',),
        }),
    )


class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'location')


admin.site.register(Slide, SlideAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Location)
