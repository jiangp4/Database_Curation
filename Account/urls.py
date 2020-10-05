from django.urls import path
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('curator_create/', views.CuratorCreateView.as_view(), name='curator_create'),
    path('curator_update/', views.CuratorUpdateView.as_view(), name='curator_update'),
    path('curator_update_complete/', views.curator_update_complete, name='curator_update_compete'),
    
    path('curator_detail/<str:username>/', views.CuratorDetailView.as_view(), name='curator_detail'),
    
    path('password/', RedirectView.as_view(url='/accounts/password_reset/'), name='password_reset'),
]
