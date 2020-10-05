import os
import re
import json
import pandas

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http.response import JsonResponse
from django.urls.base import reverse_lazy
from django.shortcuts import redirect

from Account.models import Curator
from Curation.models import Curation

from .models import Project, Association_Project_Curator, TaskUpload
from .forms import ProjectCreateForm, ProjectUpdateForm, ProjectDeleteForm, TaskUploadForm
from .utils import parse_keywords

from Database_Curation.settings import data_path

from Database.tasks import prepare_curation_list
from celery.result import AsyncResult
from Project.models import Association_Project_Dataset
from Database.models import Dataset



class ProjectCreateView(generic.CreateView):
    form_class = ProjectCreateForm
    
    template_name = 'form.html'
    
    def get_initial(self):
        projects = Project.objects.all()
        
        max_ID = max([v.ID for v in projects])
        
        return {
            'ID': max_ID + 1,
        }
    
    def get_success_url(self):
        return reverse_lazy('project_create_complete', kwargs={'ID': self.object.ID})
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create a new project"
        context['button'] = "Create"
        return context



def project_create_complete(request, ID):
    project = Project.objects.get(pk=ID)
    
    # set up owner as its own curator
    Association_Project_Curator.objects.create(
        project = project,
        curator = Curator.objects.get(pk=request.user.id),
        owner = True,
        active = False,
        )
    
    return render(request, 'complete.html', {'title': 'project create complete', 'description': 'Please select project if necessary.'})



class ProjectUpdateView(generic.UpdateView):
    form_class = ProjectUpdateForm
    
    fail_url = reverse_lazy('project_select')
    
    template_name = 'form.html'
    
    def get_object(self):
        # we assume the main template will not guide to here if project not selected
        project_select = self.request.session.get('project_select')
        assert project_select is not None
        
        return get_object_or_404(Project, pk=project_select)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Update project % s" % self.object
        context['button'] = "Update"
        return context
    
    
    def form_valid(self, form):
        self.keyword_change = int('keywords' in form.changed_data)
        
        return super(ProjectUpdateView, self).form_valid(form)
    
    
    def get_success_url(self):
        return reverse_lazy('project_update_complete', kwargs={'flag': self.keyword_change})



def filter_project_dataset_by_keywords(project):
    associations = Association_Project_Dataset.objects.filter(project=project, dataset__status = 'Regular')
    
    if not project.keywords_filter:
        associations.update(active=True)
        return
    
    keywords = parse_keywords(project.keywords, flag_Chrome=True, flag_addstart=True).split(',')
    
    for i in range(len(keywords)): keywords[i] = re.compile(keywords[i].strip(), re.IGNORECASE)   # @UndefinedVariable
    
    for association in associations:
        dataset = association.dataset
        flag = False
        
        for v in [dataset.title, dataset.summary, dataset.design]:
            for keyword in keywords:
                if keyword.search(v) is not None:
                    flag = True
                    break
            
            if flag: break
        
        if not flag:
            meta_info = os.path.join(data_path, dataset.database, 'Data', dataset.ID, dataset.ID + '.meta')
                        
            fin = open(meta_info)
            for l in fin:
                for keyword in keywords:
                    if keyword.search(l) is not None:
                        flag = True
                        break
                
                if flag: break
            fin.close()
        
        association.active = flag
        association.save()
        
        



def project_update_complete(request, flag):
    project = Project.objects.get(pk = request.session['project_select'])
    
    # only filter data if the keyword filters are changed
    if flag: filter_project_dataset_by_keywords(project)
    
    return render(request, 'project/project_update_complete.html')



class ProjectDeleteView(generic.DeleteView):
    form_class = ProjectDeleteForm
    
    success_url = reverse_lazy('project_delete_complete')
    template_name = 'project/project_delete.html'
    
    def get_object(self):
        # we assume the main template will not guide to here if project not selected
        project_select = self.request.session.get('project_select')
        assert project_select is not None
        
        return get_object_or_404(Project, pk=project_select)



def project_delete_complete(request):
    return render(request, 'project/project_delete_complete.html')



def project_select(request):
    # Select the current project to work on
    
    if request.is_ajax() and request.method == 'POST':
        # Submit a form with annotation information
        table = json.loads(request.body).get('table')
        
        if table is None:
            response = JsonResponse({"error": "table data not exists for project selection"})
            response.status_code = 500
            return response
        
        table = pandas.DataFrame(table).dropna()
        
        if 'ID' not in table.columns:
            response = JsonResponse({"error": "ID columns does not exist in the table for project selection"})
            response.status_code = 500
            return response
        
        table.index = table['ID']
        table.drop('ID', axis=1, inplace=True)
        
        project_select = table.index[table['Select'] == True]
        
        if len(project_select) == 0:
            response = JsonResponse({"error": "Please select a project."})
            response.status_code = 500
            return response
        
        elif len(project_select) > 1:
            response = JsonResponse({"error": "We don't support selecting multiple projects for now."})
            response.status_code = 500
            return response
        
        project_select = Project.objects.filter(ID = int(project_select[0]))
        assert project_select.count() == 1
        
        project_select = project_select[0].ID
        
        request.session['project_select'] = project_select
        
        # clear up all previous active projects, assuming failed shutdown and duplicated login could exist to mess up the project selection
        Association_Project_Curator.objects.filter(curator__username = request.user.username, active = True).update(active = False)
        
        # save the current project to be True
        associations = Association_Project_Curator.objects.filter(curator__username = request.user.username, project__ID = project_select)
        
        # don't allow multiple projects status
        assert associations.count() == 1
        
        associations.update(active = True)
        request.session['project_select_owner'] = associations[0].owner
        
        request.session.modified = True
        
        # record every thing into the database
        return JsonResponse({"message": "Project selected!", "success_url": "/curation/dataset/"})    
    
    
    # any existing project selection
    project_select = request.session.get('project_select')
    
    data_map = {}
    
    # column index to return back
    data_map['title'] = 'Project Selection'
    
    data_map['header'] = [
        ['ID', 'text', ''],
        ['Title', 'text', ''],
        ['Summary', 'text', ''],
        ['Select', 'radio', 'Select the project that you want to work on'],
        ]
    
    data_map['table'] = data = []
    
    #projects = Project.objects.all()
    associations = Association_Project_Curator.objects.filter(curator__username = request.user.username)
    projects = [association.project for association in associations]
    
    for project in projects:
        lst = [
            [project.ID, 'number', ''],
            [project.title, 'text', ''],
            [project.description, 'text', ''],
            ['checked' if project.ID == project_select else '', 'radio', 'project_select'],
        ]
        
        # correct potential bad characters for csv
        for entry in lst:
            if entry[1] == 'text': entry[0] = entry[0].replace('\"', '')
            
        data.append(lst)
    
    return render(request, 'table.html', {'data' : data_map, 'title': 'Please select a project to work on.', 'flag_tight': True})




def project_assign_curator(request):
    
    project = request.session.get('project_select')
    
    # the main template should guarantee this: you can only select project with owner login
    assert project is not None
    
    
    if request.is_ajax() and request.method == 'POST':
        # Submit a form with annotation information
        table = json.loads(request.body).get('table')
        assert table is not None
        
        table = pandas.DataFrame(table).dropna()
        assert 'Username' in table.columns
        
        table.index = table['Username'].apply(lambda v:v.split('\n')[0].split('\t')[0])
        
        # remove these unchecked users
        user_remove = table.index[~table['Select']]
        
        for username in user_remove:
            Association_Project_Curator.objects.filter(project__ID = project, curator__username = username).delete()
        
        # record every thing into the database
        return JsonResponse({"message": "Curators successfully modified"})
    
    
    message = None
    
    
    if 'curator_username' in request.POST:
        username = request.POST['curator_username']
        
        if username == request.user.username:
            message = 'Error: You are by default a curator of your project. Please select someone else.'
            
        else:
            curator = Curator.objects.filter(username = username)
                
            if curator.count() == 0:
                message = 'Error: Cannot find user name %s. Please check again.' % username
            else:
                assert curator.count() == 1
                curator = curator[0]
                
                associations = Association_Project_Curator.objects.filter(project__ID = project, curator__username = curator.username)
                
                if associations.count() > 0:
                    message = 'Error: %s is already a existing curator. Please select someone else.' % curator
                
                else:
                    Association_Project_Curator.objects.create(
                        project = Project.objects.get(ID = project),
                        curator = curator,
                        owner = ('add_owner_checkbox' in request.POST) and (request.POST['add_owner_checkbox'] == 'on'),
                        active=False
                        )
                    
                    message = 'Successfully add %s as a curator' % (curator)
    
    # get existing curators
    data = {}
    data['header'] = ['Username', 'ID', 'Name', 'Institute', 'Owner', 'Select']
    curator_lst = data['table'] = []
    
    associations = Association_Project_Curator.objects.filter(project__ID = project)
    
    for association in associations:
        curator = association.curator
        
        curator_lst.append([
            [curator.username, '/accounts/curator_detail/%s/' % curator.username],
            curator.id,
            curator.first_name + ' ' + curator.last_name,
            curator.institute,
            association.owner,
            
            # you cannot delete your self
            'disabled' if request.user.username == curator.username else '',
            ])
    
    return render(request, 'project/project_assign_curator.html', {
        'title': Project.objects.get(ID = project).title,
        'message': message,
        'data': data
        })


# show the list of current public projects
def project_list(request):
    
    data_map = {}
    
    # column index to return back
    data_map['title'] = 'Public projects'
    
    data_map['header'] = [
        ['ID', 'text', ''],
        ['Title', 'text', ''],
        ['Summary', 'text', ''],
        ['Fields', 'text', ''],
        ['Contacts', 'text', ''],
        ]
    
    data_map['table'] = data = []
    
    data_map['simple_mode'] = True
    
    projects = Project.objects.filter(public=True)
    
    for project in projects:
        owners = Association_Project_Curator.objects.filter(project=project, owner=True)
        email_lst = [owner.curator.email for owner in owners]
        
        lst = [
            [project.ID, 'number', ''],
            [project.title, 'text', ''],
            [project.description, 'text', ''],
            [project.fields, 'text', ''],
            [ ', '.join(email_lst), 'text', ''],
        ]
        
        # correct potential bad characters for csv
        for entry in lst:
            if entry[1] == 'text': entry[0] = entry[0].replace('\"', '')
        
        data.append(lst)
    
    return render(request, 'table.html', {'data' : data_map, 'title': 'Public projects.', 'flag_tight': True})



class TaskUploadView(generic.CreateView):
    form_class = TaskUploadForm
    
    template_name = 'project/task_upload.html'
    
    def get_context_data(self, **kwargs):
        current_project = self.request.session['project_select']
        
        task_uploads = TaskUpload.objects.filter(project=current_project)
        
        associations = Association_Project_Curator.objects.filter(project=current_project, owner=False)
        curators = []
        
        for association in associations:
            curator = association.curator
            curators.append([
                [curator.username, '/accounts/curator_detail/%s/' % curator.username],
                '%s %s' % (curator.first_name, curator.last_name),
                curator.institute,
                ])
        
        context = super().get_context_data(**kwargs)
        
        if task_uploads.count() > 0:
            context['history'] = task_uploads
        
        if len(curators) > 0:
            context['curator'] = curators
        
        return context

    
    def get_initial(self):      
        return {
            'creator':  self.request.user,
            'project': self.request.session['project_select'],
            }
    
    def get_success_url(self):
        return reverse_lazy('task_upload_download', kwargs={'pk': self.object.pk})



def task_upload_download(request, pk):
    task_upload = TaskUpload.objects.get(pk=pk)
    f = task_upload.task_file.path
    
    project = request.session.get('project_select')
    
    GEO_search = AE_search = ID_list = None
    
    if task_upload.file_type == 'GEO': GEO_search = f
    
    elif task_upload.file_type == 'ArrayExpress': AE_search = f
    
    elif task_upload.file_type == 'List': ID_list = f
    
    else:
        assert False # impossible to get here
    
    curators = task_upload.curator.strip()
    
    if len(curators) == 0:
        curators = []
    else:
        curators = curators.split('\n')
        curators = [Curator.objects.get(username=curator.strip()) for curator in curators]
    
    # first, clear all previous empty assignments
    for curator in curators:
        Curation.objects.filter(project=project, curator=curator, category='').delete()
    
    result = prepare_curation_list.delay(GEO_search, AE_search, ID_list, project=project, curators = [curator.pk for curator in curators], flag_add_delete = task_upload.add)   # @UndefinedVariable
    
    return render(request, 'project/task_upload_download.html', {'task_id': result.task_id, 'title': task_upload.title})




def task_upload_clear(request):
    project = request.session.get('project_select')
    
    task_uploads = TaskUpload.objects.filter(project=project)
    #count = len(task_uploads)
    
    for task in task_uploads:
        if os.path.exists(task.task_file.path): os.remove(task.task_file.path)
    
    task_uploads.delete()
    
    #render(request, 'complete.html', {'title': 'Successfully clear up upload history', 'description' : '%d files deleted' % count})
    return redirect('/project/task_upload/')    



def task_upload_complete(request, task_id):
    result = AsyncResult(task_id)
    result = result.get()
    
    result, error = result
    
    project = Project.objects.get(pk=request.session['project_select'])
    
    if len(result) > 0:
        for dataset_id in result:
            Association_Project_Dataset.objects.get_or_create(
                project = project,
                dataset = Dataset.objects.get(pk=dataset_id),
            )
        
        # test if keyword filter is necessary
        filter_project_dataset_by_keywords(project)
    
    
    return render(request, 'complete.html', {
        'title': 'Task upload complete',
        'description': '%d datasets uploaded' % len(result),
        'fail': error,
        })
