import os

from django.http.response import FileResponse, HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import AnonymousUser

from Project.models import Association_Project_Curator

from Database_Curation.settings import data_path

def send_file(request, f):
    f = os.path.join(data_path, f)
    
    if os.path.exists(f):
        return FileResponse(open(f, 'rb'))
    else:
        return render(request, 'error.html', {'message': 'File does not exist %s' % os.path.basename(f)})
    
    
def send_file_delete(request, f):
    f = os.path.join(data_path, f)
    
    if os.path.exists(f):
        fin = open(f)
        s = fin.read()
        fin.close()
        
        os.remove(f)
        
        response = HttpResponse(s, content_type="text/plain")
        response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
        return response
    else:
        return render(request, 'error.html', {'message': 'File does not exist %s' % os.path.basename(f)})



def index(request):
    # load user information
    if request.user != AnonymousUser():
        project = request.session.get('project_select')
        
        # search for previous project
        if project is None:
            associations = Association_Project_Curator.objects.filter(curator__username = request.user.username, active = True)
            
            # currently, only support unique project selection
            assert len(associations) <= 1
            
            if len(associations) > 0:
                request.session['project_select'] = associations[0].project.ID
                request.session['project_select_owner'] = associations[0].owner
    
    return render(request, 'index.html')


def help_tutorial(request, section):
    return render(request, 'help/%s.html' % section)

def statistics(request):
    return render(request, 'statistics.html')
