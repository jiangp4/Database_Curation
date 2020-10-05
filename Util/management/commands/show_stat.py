import os, pandas
from django.core.management.base import BaseCommand#, CommandError
from Database.models import Dataset
from Database_Curation.settings import data_path
from Curation.models import Curation
from Project.models import Project
from Project.models import Association_Project_Dataset
from django.db.models.functions import Length

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Database_Curation.settings')

class Command(BaseCommand):
    help = 'Build the database data from command line'
    
    def add_arguments(self, parser):
        parser.add_argument('output', nargs='+', type=str)
    
    def handle(self, *args, **options):
        projects = Project.objects.all()
        
        datasets = Dataset.objects.annotate(processed_len=Length('processed_data')).filter(status='Regular', processed_len__gt=1)
        print(datasets.count(), 'datasets have processed data')
        
        merge = []
        
        for project in projects:
            project_path = os.path.join(data_path, 'Curation', str(project.ID))
            
            associations = Association_Project_Dataset.objects.filter(project=project)
            curations = Curation.objects.filter(project=project, active=True).exclude(category='')
            curations_Yes = curations.filter(category='Yes')
            
            samples = set()
            
            for curation in curations_Yes:
                annotation = os.path.join(project_path, str(curation.curator.id), curation.dataset.ID + '.meta')
                
                if os.path.exists(annotation):
                    annotation = pandas.read_csv(annotation, sep='\t', index_col=0)
                    if 'Treatment' not in annotation.columns or 'Condition' not in annotation.columns: continue
                    
                    annotation = annotation[['Treatment', 'Condition']].dropna()
                    samples.update(annotation.index)
            
            arr = pandas.Series(
                [
                associations.count(),
                associations.filter(active=True).count(),
                len(set([c.dataset.ID for c in curations])),
                len(set([c.dataset.ID for c in curations_Yes])),
                len(samples)
                ],
                index = ['Total', 'Keyword', 'Processed', 'Hit', 'Sample'],
                name = project.title, 
            )
            
            merge.append(arr)
        
        result = pandas.concat(merge, axis=1, join='inner').transpose()
        result.to_csv(options['output'][0] + '.csv')
