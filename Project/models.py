from django.db import models

from Database_Curation.settings import MAX_STR_LENGTH
from Account.models import Curator
from Database.models import Dataset

# Create your models here.
class Project(models.Model):
    ID = models.IntegerField('ID', primary_key = True, blank=True)
    title = models.CharField('title', max_length=MAX_STR_LENGTH)
    description = models.TextField('description', blank=True)
    
    # public visible or private project
    public = models.BooleanField('public', default=True)
    
    # whether the current project is approved
    approved = models.BooleanField('approved', default=False)
    
    fields = models.TextField('fields', blank=True)
    
    keywords = models.TextField('keywords', blank=True)
    
    # whether or not filter datasets by presense of keywords
    keywords_filter = models.BooleanField('keywords_filter', default=True)
    
    # whether or not only look at dataset with processed data
    processed_filter = models.BooleanField('processed_filter', default=False)
    
    vocabulary = models.TextField('vocabulary', blank=True)
    
    # automatic mapping for standard vocabularies
    vocabulary_map = models.TextField('vocabulary_map', blank=True)
    
    def __unicode__(self): return u'%d : %s' % (self.ID, self.title)
    def __str__(self): return self.__unicode__()



class Association_Project_Curator(models.Model):
    project = models.ForeignKey(Project, related_name='association_project_curator', on_delete=models.CASCADE)
    curator = models.ForeignKey(Curator, related_name='association_project_curator', on_delete=models.CASCADE)
    
    owner = models.BooleanField('owner')
    active = models.BooleanField('active')
    
    class Meta:
        unique_together = (('project', 'curator'),)
    
    def __unicode__(self): return "(%s, %s, %r, %r)" %(self.project, self.curator, self.owner, self.active)
    def __str__(self): return self.__unicode__()



file_types = (
    ('GEO', 'GEO query download'),
    ('ArrayExpress', 'ArrayExpress query download'),
    ('List', 'List of GEO or ArrayExpress IDs'),
)

class TaskUpload(models.Model):
    title = models.CharField('title', max_length=MAX_STR_LENGTH)
    
    task_file = models.FileField('task_file', upload_to='upload/')
    file_type = models.CharField('file_type', max_length=MAX_STR_LENGTH, choices=file_types)
    
    time_upload = models.DateTimeField('time_upload', auto_now_add=True)
    
    # add or remove uploaded dataset ID
    add = models.BooleanField('add', default=True)
    
    # history records fields
    project = models.ForeignKey(Project, related_name='file_upload', on_delete=models.CASCADE)
    creator = models.ForeignKey(Curator, related_name='file_upload', on_delete=models.CASCADE)
    
    # ID list of curators assigned
    curator = models.TextField('curator', blank=True)
    
    def __unicode__(self): return "%s, %s" % (self.title, self.task_file)
    def __str__(self): return self.__unicode__()



class Association_Project_Dataset(models.Model):
    project = models.ForeignKey(Project, related_name='association_project_dataset', on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, related_name='association_project_dataset', on_delete=models.CASCADE)
    
    # a flag to consider or not the current dataset for NLP filters
    active = models.BooleanField('active', default=True)
    
    class Meta:
        unique_together = (('project', 'dataset'),)
    
    def __unicode__(self): return "(%s, %s)" %(self.project, self.dataset)
    def __str__(self): return self.__unicode__()
