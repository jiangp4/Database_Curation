from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.widgets import TextInput, CheckboxInput
from .models import Curator


field_introductions = {
    'keywords_highlight' : CheckboxInput(attrs={'title': 'Whether or not highlight keywords in curation tables.'}),
    'show_curated' : CheckboxInput(attrs={'title': 'Whether or not show previously curated dataset in the next time.'}),    
    }

class CuratorCreateForm(UserCreationForm):
    class Meta:
        model = Curator
        fields = ('username', 'first_name', 'last_name', 'email', 'institute', 'education', 'url', 'bio', 'keywords_highlight', 'show_curated')
        
        widgets = field_introductions


class CuratorUpdateForm(UserChangeForm):
    class Meta:
        model = Curator
        fields = ('first_name', 'last_name', 'email', 'institute', 'education', 'url', 'bio', 'keywords_highlight', 'show_curated')
        
        widgets = {
            **{
                'username' : TextInput(attrs={'readonly': 'readonly'}),
               },
            **field_introductions,
        }
