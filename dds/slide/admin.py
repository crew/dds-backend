from models import Slide, Asset, Client
from django.contrib import admin

class AssetAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields' : ['file', 'content_type']}),
    ]
    list_display = ('id', 'file')

class SlideAdmin(admin.ModelAdmin):
    exclude = ['last_update']
        
    list_display = ('title', 'user', 'group', 'expires_at')

class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'location')

admin.site.register(Slide, SlideAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Client, ClientAdmin)
