from django.db import models
from django.contrib.auth.models import AbstractUser
from Database_Curation.settings import MAX_STR_LENGTH


Education_levels = (
    ('High_School', 'High school or less'),
    ('College', 'College'),
    ('Master', 'Master'),
    ('Doctor', 'Doctoral or equivalent professional degree'),
)

# Create your models here.
class Curator(AbstractUser):
    # add additional fields in here
    email = models.EmailField('email', unique=True)
    
    first_name = models.CharField('first_name', max_length = MAX_STR_LENGTH)
    last_name = models.CharField('last_name', max_length = MAX_STR_LENGTH)
    institute = models.CharField('institute', max_length = MAX_STR_LENGTH)
    education = models.CharField('education', max_length = MAX_STR_LENGTH, choices=Education_levels)
    
    url = models.URLField('url', blank=True)
    bio = models.TextField('bio', blank=True)
    
    # allowance of number of datasets in a project
    allowance = models.IntegerField('allowance', default=1000)
    
    # whether or not highlight keywords
    keywords_highlight = models.BooleanField('highlight_keywords', default=True)
    
    # whether or not show previously curated dataset in the next time
    show_curated = models.BooleanField('show_curated', default=False)
    
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'institute', 'education', 'keywords_highlight', 'show_curated']
    USERNAME_FIELD = 'username'
    
    def __str__(self): return self.username
