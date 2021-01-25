from django.contrib import admin

from .models import Project, Association_Project_Curator, Association_Project_Dataset, TaskUpload

# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('ID', 'title', 'description', 'public', 'approved', 'fields', 'keywords', 'keywords_filter', 'processed_filter', 'vocabulary', 'vocabulary_map')
    ordering = ('ID',)
    search_fields = ('ID', 'title', 'description', 'public', 'approved', 'fields', 'keywords', 'keywords_filter', 'processed_filter', 'vocabulary', 'vocabulary_map')

admin.site.register(Project, ProjectAdmin)


class Association_Project_Curator_Admin(admin.ModelAdmin):
    list_display = ('project', 'curator', 'owner', 'active')
    ordering = ('project',)
    search_fields = ('project__title', 'curator__username', 'owner', 'active')

admin.site.register(Association_Project_Curator, Association_Project_Curator_Admin)


class TaskUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_file', 'file_type', 'add', 'time_upload', 'creator', 'project', 'curator')
    ordering = ('title',)
    search_fields = ('title', 'task_file', 'file_type', 'add', 'time_upload', 'creator', 'project', 'curator')

admin.site.register(TaskUpload, TaskUploadAdmin)


class Association_Project_Dataset_Admin(admin.ModelAdmin):
    list_display = ('project', 'dataset')
    ordering = ('project',)

    search_fields = ('project__ID', 'project__title', 'dataset__ID', 'dataset__title')

admin.site.register(Association_Project_Dataset, Association_Project_Dataset_Admin)
