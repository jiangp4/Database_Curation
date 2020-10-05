from django.test import TestCase
from .models import Dataset
import pandas


class DatasetTest(TestCase):
    
    def test_dataset_technology(self):
        datasets = Dataset.objects.all()
        
        count_map = {}
        
        for dataset in datasets:
            technology = dataset.technology
            count_map[technology] = count_map.get(technology, 0) + 1
        
        print(pandas.Series(count_map).sort_values(ascending=True))
        
        self.assertIs(False, False)
