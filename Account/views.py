from django.shortcuts import render

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from Account.forms import CuratorCreateForm, CuratorUpdateForm
from Account.models import Curator


class CuratorCreateView(generic.CreateView):
    form_class = CuratorCreateForm
    success_url = reverse_lazy('login')
    template_name = 'registration/curator_create.html'


class CuratorUpdateView(generic.UpdateView):
    form_class = CuratorUpdateForm
    success_url = reverse_lazy('curator_update_compete')
    template_name = 'registration/curator_update.html'
    
    def get_object(self):
        return get_object_or_404(Curator, pk=self.request.user.id)


class CuratorDetailView(generic.DetailView):
    model = Curator
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    template_name = 'registration/curator_detail.html'



def curator_update_complete(request):
    return render(request, 'registration/curator_update_complete.html')

def curator_information(request, username):
    curator = Curator.objects.get(username=username)
    
    return render(request, 'registration/curator_information.html', {'user': curator})
