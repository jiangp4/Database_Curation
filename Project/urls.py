from django.urls import path
from . import views

urlpatterns = [
    path('project_create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project_create_complete/<int:ID>/', views.project_create_complete, name='project_create_complete'),
    
    path('project_update/', views.ProjectUpdateView.as_view(), name='project_update'),
    path('project_update_complete/<int:keyword_change>/<int:display_change>/', views.project_update_complete, name='project_update_complete'),
    
    path('project_list/', views.project_list, name='project_list'),
    
    #path('project_delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    #path('project_delete_complete/', views.project_delete_complete, name='project_delete_complete'),
    
    path('project_select/', views.project_select, name='project_select'),
    
    # only for super user
    path('project_approve/<int:ID>/', views.ProjectApproveView.as_view(), name='project_approve'),
    path('project_approve_complete/<int:ID>/<int:flag>/', views.project_approve_complete, name='project_approve_complete'),
    
    path('project_assign_curator/', views.project_assign_curator, name='project_assign_curator'),

    path('task_upload/', views.TaskUploadView.as_view(), name='task_upload'),
    
    path('task_upload_download/<int:pk>/', views.task_upload_download, name='task_upload_download'),
    
    path('task_upload_clear/', views.task_upload_clear, name='task_upload_clear'),
    
    #re_path('task_upload_complete/celery-progress/(.+)/', views.task_upload_complete, name='task_upload_complete'),
]
