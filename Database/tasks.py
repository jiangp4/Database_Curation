import os
import pandas
#import Expression_Database

#from celery import shared_task
#from celery_progress.backend import ProgressRecorder
from .models import Dataset

from Project.models import Project, Association_Project_Dataset
from Account.models import Curator
from Database_Curation.settings import data_path
from Curation.models import Curation

GEO_Path = os.path.join(data_path, 'GEO', 'Data')
AE_Path = os.path.join(data_path, 'AE', 'Data')

# From Celery
#@shared_task(bind=True)
#def prepare_curation_list(self, GEO_search, AE_search, ID_list, project=None, curators=None, flag_add_delete=True):

def prepare_curation_list(GEO_search, AE_search, ID_list, project=None, curators=None, flag_add_delete=True):
    # flag_add_delete : add (True) or delete (True) the input list
    result_lst = []
    
    error_lst = []
    
    # recover from ID (int or str) to django models, which celery cannot deal with
    if project is not None:
        project=Project.objects.get(pk=project)
    
    if curators is not None:
        curators = [Curator.objects.get(pk=curator) for curator in curators]
    
    # From Celery
    #progress_recorder = ProgressRecorder(self)
    
    # build up search list first
    GEO_included = set()
    AE_included = set()
    
    if GEO_search is not None:
        try:
            fin = open(GEO_search)
            for l in fin:
                fields = l.rstrip().split()
                if len(fields) > 0 and fields[0] == 'Series':
                    GSE_ID = l.split('Accession:')[1].strip().split()[0]
                    GEO_included.add(GSE_ID)
            fin.close()
        except:
            error_lst.append('Cannot read GEO search file')
    
    
    if AE_search is not None:
        try:
            AE_search = pandas.read_csv(AE_search, sep='\t', index_col=0, engine='python').index
            
            for v in AE_search:
                if v.find('E-GEOD') == 0:
                    GEO_included.add('GSE' + v.split('-')[-1])
                else:
                    AE_included.add(v)
        except:
            error_lst.append('Cannot read ArrayExpress search file')
    
    
    if ID_list is not None:
        try:
            fin = open(ID_list)
            for l in fin:
                did = l.strip()
                
                if did.find('GSE') == 0:
                    GEO_included.add(did)
                
                elif did.find('E-GEOD') == 0:
                    GEO_included.add('GSE' + did.split('-')[-1])
                
                else:
                    AE_included.add(did)
            
            fin.close()
            
        except:
            error_lst.append('Cannot read ID list file')
    
    ########################################################################
    # if delete these datasets (instead of add)
    if not flag_add_delete:
        ID_list = GEO_included.union(AE_included)
        
        for dataset_id in ID_list:
            # only delete un-curated items
            Curation.objects.filter(project=project, dataset__ID=dataset_id, category='').delete()
            
            # delete all!
            Association_Project_Dataset.objects.filter(project=project, dataset__ID=dataset_id).delete()
        
        return result_lst, error_lst 
    
    
    ########################################################################
    # Add datasets
    
    # GEO first
    
    # set to list, since we will dynamically add new for super-series
    GEO_included = list(GEO_included)
    
    i = 0
    
    while i < len(GEO_included):
        GSE_ID = GEO_included[i]
        i = i + 1
        
        lst = Dataset.objects.filter(ID=GSE_ID)
        
        if len(lst) > 0:
            assert len(lst) == 1 # ID is the unique key
            info = lst[0]
        else:
            # don't allow new dataset download for now
            error_lst.append('%s not included in existing datasets' % GSE_ID)
            continue
        
            """
            # no longer allow data download
            try:
                info = Expression_Database.GEO_meta(GSE_ID, os.path.join(GEO_Path, GSE_ID), flag_enforce=False)
            except Exception as _:
                info = None
            
            if info is None:
                # always write some thing
                info = Dataset.objects.create(ID=GSE_ID, database='GEO', status='Fail', count=0)
            else:
                info = Dataset.objects.create(
                    ID=GSE_ID,
                    database='GEO',
                    title = info['title'],
                    summary = info['summary'],
                    design = info['design'],
                    platform = info['platform'],
                    technology = info['technology'],
                    status = info['status'],
                    count = info['count']
                )
            """
        
        if info.status == 'Fail':
            error_lst.append(GSE_ID)
        
        elif info.status.find('Super') == 0:
            # for GEO dataset, the sub-series are recorded thus could be added
            fields = info.status.split(' ', 1)
            if len(fields) > 1:
                new_set = set(fields[1].split(',')).difference(GEO_included)
                GEO_included.extend(new_set)
            
            continue
        
        # regular data set here
        result_lst.append(GSE_ID)
        
        # insert not-curated record
        if project is not None and curators is not None and info.status=='Regular':
            for curator in curators:
                Curation.objects.get_or_create(curator=curator, project=project, dataset=info)
        
        # From Celery
        #if len(result_lst) >= max_count:
        #    error_lst.append('Stop by exceeding maximum allowance %d' % max_count)
        #    break
        #progress_recorder.set_progress(len(result_lst), len(GEO_included) + len(AE_included))
    
    
    for AE_ID in AE_included:

        lst = Dataset.objects.filter(ID=AE_ID)
        
        if len(lst) > 0:
            assert len(lst) == 1 # ID is the unique key
            info = lst[0]
        else:
            error_lst.append('%s not included in existing datasets' % AE_ID)
            continue
        
            """
            # no longer allow data download
            try:
                info = Expression_Database.AE_meta(AE_ID, os.path.join(AE_Path, AE_ID), flag_enforce=False)
            except Exception as _:
                info = None
            
            if info is None:
                info = Dataset.objects.create(ID=AE_ID, database='AE', status='Fail', count=0)
            else:
                info = Dataset.objects.create(
                    ID=AE_ID,
                    database='AE',
                    title = info['title'],
                    summary = info['summary'],
                    design = info['design'],
                    platform = info['platform'],
                    technology = info['technology'],
                    status = info['status'],
                    count = info['count']
                )
            """
        
        if info.status == 'Fail':
            error_lst.append(AE_ID)
        
        elif info.status.find('Super') == 0:
            continue
        
        
        result_lst.append(AE_ID)
        
        # insert not-curated record
        if project is not None and curators is not None and info.status=='Regular':
            for curator in curators:
                Curation.objects.get_or_create(curator=curator, project=project, dataset=info)
        
        #progress_recorder.set_progress(len(result_lst), len(GEO_included) + len(AE_included))
    
    return result_lst, error_lst




"""
# Disable this function
@shared_task(bind=True)
def download_processed_data_list(self, datasets):
    progress_recorder = ProgressRecorder(self)
    success_lst = []
    fail_lst = []
    
    RNASeq_set = set(['RNA-seq of coding RNA', 'high-throughput sequencing', 'Illumina Genome Analyzer'])
    
    i = 0
    
    for dataset in datasets:
        dataset = Dataset.objects.get(pk=dataset)
        
        if dataset.processed_data == 'Fail':
            fail_lst.append(dataset.ID)
        
        elif len(dataset.processed_data) == 0:
            
            flag_RNASeq = len(RNASeq_set.intersection(dataset.technology.split(','))) > 0
    
            matrix_list = None
            
            if dataset.database == 'GEO':
                if flag_RNASeq:
                    matrix_list = download_GEO_RNASeq(dataset.ID)
                else:
                    matrix_list = download_GEO_microarray(dataset.ID)
            
            elif dataset.database == 'ArrayExpress':
                # load in meta annotation for data column re-mapping
                meta = os.path.join(data_path, dataset.meta_info + '.full.gz')
                
                if os.path.exists(meta):
                    meta = pandas.read_csv(meta, sep='\t', index_col=0, low_memory=False)
                    
                    # assume everything is string, because data columns will be strings
                    meta.index = map(str, meta.index)
                    meta = meta.astype(str)
                
                else:
                    meta = None
                
                if flag_RNASeq:
                    matrix_list = download_ArrayExpress_RNASeq(dataset.ID, meta)
                else:
                    matrix_list = download_ArrayExpress_microarray(dataset.ID, meta)
            
            if matrix_list is None or len(matrix_list) == 0:
                dataset.processed_data = 'Fail'
                fail_lst.append(dataset.ID)
            else:
                dataset.processed_data = '\t'.join(matrix_list)
                success_lst.append(dataset.ID)
            
            dataset.save()
        
        else:
            success_lst.append(dataset.ID)
        
        i = i + 1
        progress_recorder.set_progress(i, len(datasets))
    
    # insert url
    for lst in [success_lst, fail_lst]:        
        for i in range(len(lst)):
            dataset = Dataset.objects.get(pk=lst[i])
            
            if dataset.database == 'GEO':
                url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + dataset.ID
            elif dataset.database == 'ArrayExpress':
                url = 'https://www.ebi.ac.uk/arrayexpress/experiments/' + dataset.ID
            else:
                url = ''
            
            lst[i] = [dataset.ID, url]
    
    return success_lst, fail_lst
"""
