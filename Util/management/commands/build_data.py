import os, pandas
from django.core.management.base import BaseCommand#, CommandError
from Database.models import Dataset
from Database_Curation.settings import data_path
from Curation.models import Curation
from Project.models import Project
from Project.models import Association_Project_Dataset

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Database_Curation.settings')

class Command(BaseCommand):
    help = 'Build the database data from command line'
    
    def add_arguments(self, parser):
        parser.add_argument('output', nargs='+', type=str)
    
    def get_not_curated(self, project_ID, output):
        project = Project.objects.get(pk=project_ID)
        
        #curations = Curation.objects.filter(project=project, curator_id=1, active=True).exclude(category = '')
        #print(curations.count())
    
        datasets = Association_Project_Dataset.objects.filter(project=project, active=True, dataset__status='Regular')
        datasets = [dataset.dataset for dataset in datasets]
        
        cnt = 0
        
        fout = open(output, 'w')
        for dataset in datasets:
            curations = Curation.objects.filter(dataset=dataset, project=project, active=True).exclude(category = '')
            if curations.count() > 0: continue
            
            fout.write(dataset.ID + '\n')
            cnt += 1
        fout.close()
        
        print(cnt, len(datasets))
    
    
    def handle(self, *args, **options):
        self.get_not_curated(4, options['output'][0])
        
        return
    
        cnt_thres = 10000 #options['count'][0]
        
        #Dataset.objects.all().delete()
        
        """
        included = set()
        fin = open(os.path.join(data_path, 'log', 'GEO.list.MicroArray.rerun'))
        for l in fin: included.add(l.strip())
        fin.close()
        """
    
        included = set(['GSE36202'])
        
        # , 'AE'
        for database in ['GEO']:
            database_path = os.path.join(data_path, database, 'Data')
            
            ID_lst = os.listdir(database_path)
            
            for ID in ID_lst:
                fprefix = os.path.join(database_path, ID, ID)
                
                if ID not in included: continue
                print(ID)
                        
                meta = fprefix + '.meta.summary'
                if not os.path.exists(meta): continue
                meta = pandas.read_csv(meta, sep='\t', index_col=0, header=None).iloc[:,0]
                    
                processed_lst = []
                
                # 
                for data_type in ['RNASeq', 'MicroArray']:
                    processed = fprefix + '.' + data_type + '.processed'
                    if not os.path.exists(processed) or os.path.isdir(processed): continue
                    
                    fin = open(processed)
                    for l in fin:
                        f = l.strip()
                        data = pandas.read_csv(os.path.join(database_path, ID, f), sep='\t', index_col=0)
                        if data.shape[0] >= cnt_thres: processed_lst.append(f)
                    fin.close()
                
                """
                Dataset.objects.create(
                    ID=ID,
                    database=database,
                    title = meta['title'],
                    summary = meta['summary'],
                    design = meta['design'],
                    platform = meta['platform'],
                    technology = meta['technology'],
                    status = meta['status'],
                    count = meta['count'],
                    processed_data = '\t'.join(processed_lst)
                    )
                """
                
                """
                dataset = Dataset.objects.get_or_create(ID=ID, database=database)[0]
                
                dataset.title = meta['title']
                dataset.summary = meta['summary']
                dataset.design = meta['design']
                dataset.platform = meta['platform']
                dataset.technology = meta['technology']
                dataset.status = meta['status']
                dataset.count = meta['count']
                dataset.processed_data = '\t'.join(processed_lst)
                """
                
                dataset = Dataset.objects.get(ID=ID, database=database)
                dataset.processed_data = '\t'.join(processed_lst)
                dataset.save()
