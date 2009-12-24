# vim: set shiftwidth=4 tabstop=4 softtabstop=4 :
from models import Slide, Client, ClientActivity, ClientToGroup, Location
from django.contrib import admin

class SlideAdmin(admin.ModelAdmin):
    exclude = ['last_update']
    list_display = ('title', 'user', 'group', 'expires_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'group')
        }),
        (None, {
            'fields': ('priority', 'duration', 'expires_at', 'thumbnail', 'bundle'),
        }),
    )


class ClientToGroupInline(admin.TabularInline):
    model = ClientToGroup
    extra = 5

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk', 'location', 'last_contact')
    inlines = [
        ClientToGroupInline,
    ]

admin.site.register(Slide, SlideAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Location)
admin.site.register(ClientActivity)
