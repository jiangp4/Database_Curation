from Database_Curation.settings import MAX_STR_LENGTH
from django.db import models


#Status_list = (
#    ('Regular', 'Individual study that can be parsed'),
#    ('Super', 'A set of studies'),
#    ('Fail', 'Failed'),
#)


Database_list = (
    ('GEO', 'Gene Expression Omnibus @ NCBI-NIH'),
    ('AE', 'ArrayExpress @ EMBL-EBI'),
)


class Dataset(models.Model):
    # data set abstract from either GEO or ArrayExpress
    ID = models.CharField('ID', max_length=MAX_STR_LENGTH, primary_key = True)
    
    status = models.TextField('status', default='Regular')
    
    database = models.CharField('database', max_length=MAX_STR_LENGTH, blank=True, choices = Database_list)
    title = models.TextField('title', blank=True)
    summary = models.TextField('summary', blank=True)
    design = models.TextField('design', blank=True)
    platform = models.TextField('platform', blank=True)
    technology = models.TextField('technology', blank=True)
    count = models.IntegerField('count', default = 0)
    
    # should be default location
    #meta_info = models.TextField('meta table location', blank=True)
    
    # whether or not the processed data is available
    processed_data = models.TextField('processed_data', blank=True)
    
    def __unicode__(self): return u'%s : %s' % (self.ID, self.title)
    def __str__(self): return self.__unicode__()
