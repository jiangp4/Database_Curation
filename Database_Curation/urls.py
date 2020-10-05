"""Database_Curation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, re_path, include
#from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from . import views
from django.views.generic.base import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('accounts/', include('Account.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('project/', include('Project.urls')),
    path('database/', include('Database.urls')),
    path('curation/', include('Curation.urls')),
    
    path('', include('Email.urls')),
    
    path('', views.index, name='index'),
    
    path('help/<str:section>/', views.help_tutorial, name='help'),
    
    path('statistics/', views.statistics, name='help'),
    
    path('download/<path:f>/', views.send_file, name='send_file'),
    
    path('download_delete/<path:f>/', views.send_file_delete, name='send_file_delete'),
    
    re_path(r'^celery-progress/', include('celery_progress.urls')),  # the endpoint is configurable
    
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
]

# media path for developmental server
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
