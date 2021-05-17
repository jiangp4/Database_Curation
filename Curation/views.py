import os, sys, io
import pandas
import json

from django.utils import timezone
from django.core.files.temp import NamedTemporaryFile
from django.db.models.functions import Length
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.http.response import JsonResponse
from Database_Curation.settings import data_path
from Account.models import Curator
from Project.models import Project, Association_Project_Dataset, Association_Project_Curator
from Project.utils import parse_keywords
from Database.models import Dataset
from Curation.models import Curation


# Create your views here.
@csrf_protect
def dataset_table(request):
    project_ID = request.session.get('project_select')
    
    # should be guaranteed by the main template
    if project_ID is None: return render(request, 'error.html', {'message': 'User not login or project not selected'})
    
    project = Project.objects.get(pk=project_ID)
    
    if not project.approved:
        return render(request, 'error.html', {'message': 'Project not approved.', 'GOHOME': 5})
    
    # check if user is owner
    association = Association_Project_Curator.objects.filter(project=project, curator=request.user)
    assert association.count() == 1
    flag_owner = association[0].owner
    
    
    title = project.title
    
    # Submit a form with annotation information
    if request.is_ajax() and request.method == 'POST':
        
        table = json.loads(request.body).get('table')
        
        if table is None:
            response = JsonResponse({"error": "table data not exists for %s" % title})
            response.status_code = 500
            return response
        
        table = pandas.DataFrame(table).dropna()
        
        if 'ID' not in table.columns:
            response = JsonResponse({"error": "ID columns does not exist in the table for %s" % title})
            response.status_code = 500
            return response
        
        table.index = table['ID']
        
        # parse selection status
        curation_status = table['Status']
        curation_status = curation_status.loc[curation_status.apply(lambda v: len(v) > 0)]
        
        for dataset_id, flag in curation_status.iteritems():
            comment = table.loc[dataset_id, 'Comment']
            entry, flag_created = Curation.objects.get_or_create(curator=request.user, project=project, dataset=Dataset.objects.get(pk=dataset_id))
            
            # mark new or changed elements with new time stamp
            if flag_created or entry.category != flag.title() or entry.comment != comment:
                entry.time = timezone.now()
            
            entry.category = flag.title()
            entry.comment = comment
            entry.save()
        
        # record every thing into the database
        return JsonResponse({
            "message": "Table data successfully recorded for %s" % title,
            "success_url": "/curation/summary",
            })
    
    
    if flag_owner:
        # project owner can always see all data
        associations = Association_Project_Dataset.objects.filter(project=project, dataset__status = 'Regular', active=True)
    else:
        # a regular curator can only see curation tasks assigned
        associations = Curation.objects.filter(curator = request.user, project=project, dataset__status = 'Regular', active=True)
    
    
    if project.processed_filter:
        associations = associations.annotate(processed_len=Length('dataset__processed_data')).filter(processed_len__gt=1)
    
    result_lst = [association.dataset for association in associations]
    
    curated_lst = Curation.objects.filter(curator=request.user, project=project).exclude(category = '')
    
    # map any existing curation results
    curation_map = {}
    for curation in curated_lst: curation_map[curation.dataset.ID] = curation
    
    # remove curated dataset with yes/no answer
    if not request.user.show_curated:
        result_lst = set(result_lst).difference([curation.dataset for curation in curated_lst])
    
    data_map = {}

    data_map['title'] = 'dataset information'
    
    
    # keywords highlight to facilitate curation
    if len(project.keywords) > 0 and request.user.keywords_highlight:
        data_map['keywords'] = parse_keywords(project.keywords, flag_Chrome=(request.META['HTTP_USER_AGENT'].find('Chrome') >= 0), flag_addstart=True)
    
    data_map['header'] = [
        ['ID', 'url', ''],
        ['Title', 'text', ''],
        ['Summary', 'text', ''],
        ['Design', 'text', ''],
        ['Count', 'url', 'sample counts, click to see the meta information of each sample'],
        ['Status', 'select', 'Whether the current dataset is relevant, leave empty if not sure'],
        ['Comment', 'input', 'If you have anything to tell.']
        ]
    
    data_map['table'] = data = []
    
    for dataset in result_lst:    
        if dataset.database == 'GEO':
            url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + dataset.ID
        elif dataset.database == 'AE':
            url = 'https://www.ebi.ac.uk/arrayexpress/experiments/' + dataset.ID
        else:
            url = ''
        
        # load any previous annotations
        curation_previous = curation_map.get(dataset.ID)
        
        if curation_previous is None:
            category_previous = comment_previous = ''
        else:
            category_previous = curation_previous.category
            comment_previous = curation_previous.comment
        
        
        lst = [
            [dataset.ID, 'url', url],
            [dataset.title, 'text', ''],
            [dataset.summary, 'text', ''],
            [dataset.design + '\t@\t' + dataset.platform, 'text', ''],
            [dataset.count, 'url', '/curation/sample/%s@%s/' %(dataset.database, dataset.ID)],
            [category_previous, 'select', ''],
            [comment_previous, 'input', ''],
            ]
        
        # correct potential bad characters for csv
        for entry in lst:
            if entry[1] == 'text': entry[0] = entry[0].replace('\"', '')
            
        data.append(lst)
    
    return render(request, 'table.html', {'data' : data_map, 'title': 'Candidate datasets of project %s' % project})




def summary_statistics(request):
    project_ID = request.session.get('project_select')
    if project_ID is None: return render(request, 'error.html', {'message': 'User not login or project not selected'})
    
    project = Project.objects.get(pk=project_ID)
    
    association = Association_Project_Curator.objects.filter(project=project, curator=request.user)
    assert association.count() == 1
    
    association = association[0]
    assert association.active
    
    is_owner = association.owner
    
    stat_map = {}
    
    associations = Association_Project_Dataset.objects.filter(project=project, dataset__status = 'Regular')
    
    stat_map['total'] = associations.count()
    stat_map['active'] = associations.filter(active=True).count()
    stat_map['header'] = ['Curator', 'Owner', 'Curated', 'Positive']
    stat_map['table'] = data = []
    
    if is_owner:
        associations = Association_Project_Curator.objects.filter(project=project)
        curators = [association.curator for association in associations]
    else:
        curators = [request.user]
    
    curations = Curation.objects.filter(project=project).exclude(category = '')
    
    for curator in curators:
        curations_sub = curations.filter(curator=curator)
        
        lst = Association_Project_Curator.objects.filter(project=project, curator=curator)
        assert lst.count() == 1
        
        data.append([[curator.username, curator], lst[0].owner, curations_sub.count(), curations_sub.filter(category='Yes').count()])
    
    return render(request, 'curation/summary_statistics.html', {'stat_map' : stat_map, 'title': 'Curation statistics of %s' % project})




@csrf_protect
def sample_table(request, title, curator=None):
    ####################################################################################
    # initial start annotation
    database, ID = title.split('@', 1)
    
    # current project
    project_select = request.session.get('project_select')
    if project_select is None: return render(request, 'error.html', {'message': 'User not login or project not selected'})
    
    project_select = Project.objects.get(ID=project_select)
    
    if not project_select.approved: return render(request, 'error.html', {'message': 'Project not approved.', 'GOHOME': 5})
    
    
    if curator is None: curator = request.user.id
    
    # annotation output
    fpath = os.path.join(data_path, 'Curation', str(project_select.ID), str(curator))
    
    meta_annotation = os.path.join(fpath, ID + '.meta')
    
    ####################################################################################
    # if there is a data annotation submission
    if request.is_ajax() and request.method == 'POST':
        
        # Submit a form with annotation information
        table = json.loads(request.body).get('table')
        
        if table is None:
            response = JsonResponse({"error": "table data not exists for %s" % title})
            response.status_code = 500
            return response
        
        table = pandas.DataFrame(table).dropna()
        
        if 'ID' not in table.columns:
            response = JsonResponse({"error": "ID columns does not exist in the table for %s" % title})
            response.status_code = 500
            return response
        
        table.index = table['ID']
        table.drop('ID', axis=1, inplace=True)
        
        if not os.path.exists(fpath): os.makedirs(fpath)
        
        table.to_csv(meta_annotation, sep='\t')
        
        # sample table save will also trigger time update
        
        entry = Curation.objects.get_or_create(curator=Curator.objects.get(pk=curator), project=project_select, dataset=Dataset.objects.get(pk=ID))[0]
        entry.time = timezone.now()
        entry.save()
        
        # record every thing into the database
        return JsonResponse({"message": "Table data successfully recorded for %s" % title})
    
    
    ####################################################################################
    # data record for template rendering
    data_map = {}
    
    meta_info = os.path.join(data_path, database, 'Data', ID, ID + '.meta')
    
    if not os.path.exists(meta_info):
        render(request, 'error.html', {'message': 'Meta information is unavailable for ' + ID})
    
    # don't provide the full table since the existing columns should be enough
    #if os.path.exists(meta_info + '.full.gz'): data_map['full_table'] = meta_info + '.full.gz'
    
    if os.path.exists(meta_annotation):
        meta_annotation = pandas.read_csv(meta_annotation, sep='\t', index_col=0)
        meta_annotation.fillna('', inplace=True)
    else:
        meta_annotation = None
    
    meta_info = pandas.read_csv(meta_info, sep='\t')
    
    # column index to return back
    data_map['title'] = 'sample information ' + ID
    data_map['column_annotate'] = True  # automatic detect input fields in the header
    data_map['header'] = header = []
    data_map['table'] = data = []
    
    for v in meta_info.columns: header.append([v, 'text', ''])
    
    if len(project_select.keywords) > 0 and request.user.keywords_highlight:
        data_map['keywords'] = parse_keywords(project_select.keywords, flag_Chrome=(request.META['HTTP_USER_AGENT'].find('Chrome') >= 0), flag_addstart=True)
    
    if len(project_select.vocabulary) > 0:
        data_map['vocabulary'] = parse_keywords(project_select.vocabulary, white_space = None)
    
    # only Chrome support look ahead behind features
    flag_Chrome = request.META['HTTP_USER_AGENT'].find('Chrome') > 0
    
    if len(project_select.vocabulary_map) > 0:
        vocabulary_map = data_map['vocabulary_map'] = {}
        
        sin = io.StringIO(project_select.vocabulary_map)
        for l in sin:
            l = l.strip()
            if len(l) == 0 or l[0] in ['#']: continue
            
            fields = l.split(':', 1)
            
            if len(fields) != 2:
                sys.stderr.write('Wrong format of vocabulary map line %s\n' % l)
                continue
            
            pattern, target = fields
            
            # use \t as separator not happen
            pattern = parse_keywords(pattern.strip(), sep='\t')
            target = target.strip()
            
            if flag_Chrome:
                pattern = '(^|(?<=[ +&]))((%s)|(%s))($|(?=[ +&]))' % (pattern, target)
            else:
                pattern = '^((%s)|(%s))($|(?=[ +&]))' % (pattern, target)
            
            vocabulary_map[pattern] = target
        
        sin.close()

    
    fields = project_select.fields.strip()
    
    if len(fields) > 0:
        fields = fields.split(',')    
        for i in range(len(fields)): fields[i] = fields[i].strip()
    else:
        fields = []
    
    # if added extra column in the previous annotation
    if meta_annotation is not None:
        for title in meta_annotation.columns:
            if title not in fields: fields.append(title)
    
    # load in header columns
    for i in range(len(fields)): header.append([fields[i], 'input', ''])
    
    # standardize the column names
    meta_info.columns = [v.upper() for v in meta_info.columns]
    
    for _, arr in meta_info.iterrows():
        
        lst = []
        
        for v in arr:
            if database == 'GEO' and v == arr.iloc[0]:
                url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + v
                lst.append([v, 'url', url])
            else:    
                lst.append([v, 'text', ''])
        
        for title in fields:        
            if meta_annotation is not None:
                # if previous annotation exists
                try:
                    v = meta_annotation.loc[arr.loc['ID'], title]
                    
                except KeyError:
                    v = ''
            
            elif title.upper() in arr.index:
                # if existing value exists
                v = arr[title.upper()]
                
            else:
                v = ''
                
            lst.append([v, 'input', title])
        
        data.append(lst)
        
    return render(request, 'table.html', {'data' : data_map, 'title': 'Sample information of ' + ID})




def result_table(request):
    # current project
    project_select = request.session.get('project_select')
    if project_select is None: return render(request, 'error.html', {'message': 'User not login or project not selected'})
    
    project_select = Project.objects.get(ID=project_select)
    
    curations = Curation.objects.filter(project=project_select, category__in = ['Yes', 'No'], active=True)
    
    # result path for project_select
    project_path = os.path.join(data_path, 'Curation', str(project_select.ID))
    
    if request.is_ajax() and request.method == 'POST':
        action = json.loads(request.body).get('action')
        
        if action == 'submit':
            # First, see the table
            table = json.loads(request.body).get('table')
            
            if table is None:
                response = JsonResponse({"error": "table data not exists in the result"})
                response.status_code = 500
                return response
            
            table = pandas.DataFrame(table).dropna()
            
            if 'ID' not in table.columns:
                response = JsonResponse({"error": "ID column does not exist in the result table"})
                response.status_code = 500
                return response
            
            for _, arr in table.iterrows():
                entry = curations.filter(dataset__ID = arr['ID'], curator__username = arr['Curator'])
                assert entry.count() == 1   # defined by the constraint require in model
                
                entry = entry[0]
                
                if arr['Revisit']:
                    entry.category = ''
                    entry.validated = False
                else:
                    entry.validated = arr['Validated']
                
                entry.save()
                
            
            return JsonResponse({
                "message": "Table label submitted.",
            })
        
        elif action == 'download':
        
            # Second, download data URLs
            file_list = NamedTemporaryFile(prefix='result_for_%s_' % request.user.username, suffix='.txt', dir=project_path, delete=False)
            
            fout = open(file_list.name, "w")
            
            # part 1 : meta data annotation
            datasets = set()
            
            curations = curations.filter(category='Yes')
            
            for curation in curations:
                meta_annotation = os.path.join(project_path, str(curation.curator.id), curation.dataset.ID + '.meta')
                
                if os.path.exists(meta_annotation):
                    fout.write(request.build_absolute_uri('/download/%s' % os.path.relpath(meta_annotation, data_path)) + '\n')
                    datasets.add(curation.dataset)
            
            # part 2 : data matrix
            for dataset in datasets:
                if len(dataset.processed_data) > 0 and dataset.processed_data != 'Fail':
                    processed_data_lst = dataset.processed_data.split('\t')
                    
                    for f in processed_data_lst:
                        fout.write(request.build_absolute_uri('/download/%s' % os.path.join(dataset.database, 'Data', dataset.ID, f)) + '\n')
            
            fout.close()
            
            return JsonResponse({
                "message": "",
                "success_url": '/download_delete/' + os.path.relpath(file_list.name, data_path) + '/',
                })
        
        else:
            return JsonResponse({"message": "unknown actions"})
    
    
    data_map = {'flag_longwait': True}

    data_map['title'] = 'Curated dataset information'
    
    data_map['header'] = [
        ['ID', 'url', ''],
        ['Title', 'text', ''],
        #['Summary', 'text', ''],
        #['Design', 'text', ''],
        ['Count', 'url', 'sample counts, click to see the meta information of each sample'],
        ['Curator', 'text', ''],
        ['Category', 'url', 'Annotation category with URL to annotation data if available'],
        ['Processed Data', 'url', 'Whether the processed data is available.'],
        ['Time', 'text', ''],
        ['Comment', 'text', ''],
        ['Validated', 'check', ''],
        
        ['Revisit', 'check', 'Send back these datasets to curators to re-annotate'],
        ]
    
    data_map['table'] = data = []
    
    for curation in curations:
        
        if curation.dataset.database == 'GEO':
            url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + curation.dataset.ID
        elif curation.dataset.database == 'AE':
            url = 'https://www.ebi.ac.uk/arrayexpress/experiments/' + curation.dataset.ID
        else:
            url = ''
        
        meta_annotation = os.path.join('Curation', str(project_select.ID), str(curation.curator.id), curation.dataset.ID + '.meta')
        
        flag_meta_annotation = os.path.exists(os.path.join(data_path, meta_annotation))
        
        flag_processed_data = len(curation.dataset.processed_data) > 0 and curation.dataset.processed_data != 'Fail'
        
        url_sample_annotation = '/download/%s/' % meta_annotation
        
        url_processed_data = []
        
        if flag_processed_data:
            lst = curation.dataset.processed_data.split('\t')
            for f in lst:
                url_processed_data.append([f, '/download/%s/' % os.path.join(curation.dataset.database, 'Data', curation.dataset.ID, f)])
        
        lst = [
            [curation.dataset.ID, 'url', url],
            [curation.dataset.title, 'text', ''],
            #[curation.dataset.summary, 'text', ''],
            #[curation.dataset.design + '\t@\t' + curation.dataset.platform, 'text', ''],
            [curation.dataset.count, 'url', '/curation/sample/%s@%s/%d/'% (curation.dataset.database, curation.dataset.ID, curation.curator.id)],
            [curation.curator.username, 'url', '/accounts/curator_detail/%s/' % curation.curator.username],
            [curation.category, 'url', url_sample_annotation if flag_meta_annotation else ''],
            [flag_processed_data, 'url_lst', url_processed_data],
            [curation.time, 'time', ''],
            [curation.comment, 'text', ''],
            ['checked' if curation.validated else '', 'check', ''],
            
            ['', 'check', ''],
            ]
        
        # correct potential bad characters for csv
        for entry in lst:
            if entry[1] == 'text': entry[0] = entry[0].replace('\"', '')
            
        data.append(lst)
    
    return render(request, 'table.html', {
        'data' : data_map,
        'title': 'Curated datasets of project %s' % project_select,
        'flag_download': True,
        'flag_tight': True,
        })
