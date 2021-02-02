from django.shortcuts import render

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from Account.forms import CuratorCreateForm, CuratorUpdateForm
from Account.models import Curator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


class CuratorCreateView(generic.CreateView):
    form_class = CuratorCreateForm
    success_url = reverse_lazy('curator_create_compete')
    template_name = 'registration/curator_create.html'
    
    def form_valid(self, form):
        
        if self.request.is_secure():
            http = 'https'
        else:
            http = 'http'
        
        current_site = '%s://%s' % (http, self.request.META['HTTP_HOST'])
        
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        
        mail_subject = 'Activate your account.'
        
        message = render_to_string('registration/activate_email.html',
            {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                #'token': default_token_generator.make_token(user),
            },
        )
        
        to_email = form.cleaned_data.get('email')
        
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        
        return super(CuratorCreateView, self).form_valid(form)



def activate(request, uidb64):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Curator.objects.get(pk=uid)
    
    except(TypeError, ValueError, OverflowError, Curator.DoesNotExist):
        user = None
    
    #  and default_token_generator.check_token(user, token)
    if user is not None:
        user.is_active = True
        user.save()
    
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid!')



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


def curator_create_complete(request):
    return render(request, 'complete.html', {'title': 'User account create complete', 'description': 'Please login to access your account.'})


def curator_update_complete(request):
    return render(request, 'complete.html', {'title': 'User account update complete', 'description': 'Successful user information change of %s' % request.user.username})


def curator_information(request, username):
    curator = Curator.objects.get(username=username)
    
    return render(request, 'registration/curator_information.html', {'user': curator})
