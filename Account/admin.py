from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CuratorCreateForm, CuratorUpdateForm
from .models import Curator

class CuratorAdmin(UserAdmin):
    model = Curator
    add_form = CuratorCreateForm
    form = CuratorUpdateForm
    
    ordering = ('username',)
    list_display = ['id', 'username', 'first_name', 'last_name', 'email', 'institute', 'education', 'url', 'bio', 'allowance', 'keywords_highlight', 'show_curated']
    search_fields = ('username', 'first_name', 'last_name', 'email', 'institute', 'education', 'bio', 'allowance', 'keywords_highlight', 'show_curated')
    
    def change_view(self, request, object_id):
        # we want to limit the ability of the normal user to edit permissions.
        if request.user.is_superuser:
            self.fieldsets = (
                (None, {'fields': ('username', 'password')}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'education', 'url', 'bio', 'keywords_highlight', 'show_curated')}),
                ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions', 'allowance')}),
                ('Important dates', {'fields': ('last_login', 'date_joined')}),
                ('Groups', {'fields': ('groups',)}),
            )
        else:
            self.fieldsets = (
                (None, {'fields': ('username', 'password')}),
                ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'education', 'url', 'bio', 'keywords_highlight', 'show_curated')}),
                ('Important dates', {'fields': ('last_login', 'date_joined')}),
            )

        return super(UserAdmin, self).change_view(request, object_id,)
    
admin.site.register(Curator, CuratorAdmin)
