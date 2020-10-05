from django.contrib import admin

# Register your models here.
from Database.models import Dataset


class DatasetAdmin(admin.ModelAdmin):
    list_display =  ('ID', 'database', 'title', 'summary', 'design', 'platform', 'technology', 'count', 'status', 'processed_data')
    ordering = ('-count',)
    search_fields = ('ID', 'database', 'title', 'summary', 'design', 'platform', 'technology', 'count', 'status', 'processed_data')

admin.site.register(Dataset, DatasetAdmin)
