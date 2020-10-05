from django.contrib import admin
from .models import Curation

class CurationAdmin(admin.ModelAdmin):
    list_display = ('curator', 'project', 'dataset', 'category', 'comment', 'active', 'validated', 'time')
    ordering = ('project',)
    
    search_fields = ('curator__username', 'project__title', 'dataset__ID', 'dataset__title', 'category', 'comment', 'time')

admin.site.register(Curation, CurationAdmin)
