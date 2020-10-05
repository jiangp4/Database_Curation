from django.urls import path
from . import views

urlpatterns = [
    path('dataset/', views.dataset_table, name='curation_table'),
    path('sample/<str:title>/', views.sample_table, name='curation_sample'),
    path('sample/<str:title>/<int:curator>/', views.sample_table, name='curation_sample'),
    
    path('result/', views.result_table, name='curation_result'),    
    path('summary/', views.summary_statistics, name='curation_summary_statistics'),
]
