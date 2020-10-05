from django.db import models

# Create your models here.
from Project.models import Project
from Account.models import Curator
from Database.models import Dataset
from Database_Curation.settings import MAX_STR_LENGTH

curation_status_list = (
    ('Yes', 'Yes'),
    ('No', 'No'),
    ('', 'Undetermined'),
)

class Curation(models.Model):
    curator = models.ForeignKey(Curator, related_name='curation', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='curation', on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, related_name='curation', on_delete=models.CASCADE)
    
    # curation results
    category = models.CharField('category', max_length=MAX_STR_LENGTH, default = '', choices = curation_status_list)
    
    comment = models.TextField('comment', blank=True)
    
    # a option to freeze down curation assignments
    active = models.BooleanField('active', default=True)
    
    # whether the curation decision is validated by the independent person
    validated = models.BooleanField('validated', default=False)
    
    time = models.DateTimeField('time', auto_now_add=True)
    
    class Meta:
        unique_together = (('curator', 'project', 'dataset'),)
    
    def __unicode__(self): return "%s, %s, %s" % (self.curator, self.project, self.dataset)
    def __str__(self): return self.__unicode__()
