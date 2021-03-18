from django.forms import ModelForm, CharField
from django.forms.widgets import TextInput, CheckboxInput, HiddenInput, Textarea

from .models import Project, TaskUpload


field_introductions = {
    'ID' : TextInput(attrs={'readonly': 'readonly', 'title': 'Automatically generated ID, cannot change.'}),
    'public' : CheckboxInput(attrs={'title': 'Whether or not this project is publically visible.'}),
    
    'approved' : CheckboxInput(attrs={'disabled': True, 'title': 'Whether of not this project is approved by the administrator.'}),
    
    'fields' : TextInput(attrs={'title': 'Default curation fields in the sample annotation separated by ,'}),
    'keywords' : Textarea(attrs={'title': 'keywords in the sample selection separated by ,'}),
    'keywords_filter' : CheckboxInput(attrs={'title': 'Whether or not filter datasets by keywords.'}),
    'processed_filter' : CheckboxInput(attrs={'title': 'Whether or not filter datasets by processed data availability.'}),
    'vocabulary' : Textarea(attrs={'title': 'controlled vocabulary in the sample annotation separated by ,'}),
    'vocabulary_map' : Textarea(attrs={'title': 'automatic mapping from regular expressions to controlled vocabulary'}),    
    }


class ProjectApproveForm(ModelForm):
    # for super user only
    class Meta:
        model = Project
        
        fields = ('title', 'description', 'approved')
        
        widgets = {
            'title' : TextInput(attrs={'readonly': 'readonly'}),
            'description' : TextInput(attrs={'readonly': 'readonly'}),
            }
    
    # message send to project owners
    message = CharField(widget = Textarea)



class ProjectCreateForm(ModelForm):
    class Meta:
        model = Project
        fields = ('ID', 'title', 'description', 'public', 'fields', 'keywords', 'keywords_filter', 'processed_filter', 'vocabulary', 'vocabulary_map')
        widgets = field_introductions


class ProjectUpdateForm(ModelForm):
    class Meta:
        model = Project
        fields = ('ID', 'title', 'description', 'public', 'fields', 'keywords', 'keywords_filter', 'processed_filter', 'vocabulary', 'vocabulary_map')
        widgets = field_introductions


class ProjectDeleteForm(ModelForm):
    class Meta:
        model = Project
        fields = ('ID', 'title', 'description')
        
        widgets = {
            'ID' : TextInput(attrs={'readonly': 'readonly'}),
            'title' : TextInput(attrs={'readonly': 'readonly'}),
            'description' : TextInput(attrs={'readonly': 'readonly'}),
            }


class TaskUploadForm(ModelForm):
    class Meta:
        model = TaskUpload
        
        fields = ('title', 'task_file', 'file_type', 'add', 'project', 'creator', 'curator')
        
        widgets = {
            'project' : HiddenInput(),
            'creator' : HiddenInput(),
            'curator' : HiddenInput(),
            
            'add' : CheckboxInput(attrs={'title': 'add or remove datasets.'}),
            }
        
        labels = {
            'add': 'add (check) or remove (uncheck) uploaded dataset IDs',
        }
