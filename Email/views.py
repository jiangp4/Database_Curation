from django.shortcuts import render, redirect
from django.contrib.auth.models import AnonymousUser
from django.core.mail import BadHeaderError, EmailMessage
from .forms import ContactForm

from Account.models import Curator


def EmailSendView(request):
    if request.method == 'GET':
        if request.user != AnonymousUser():
            curator = Curator.objects.get(pk=request.user.id)
            form = ContactForm(initial={'from_email': curator.email})
        else:
            form = ContactForm()
    
    else:
        form = ContactForm(request.POST)
        
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            
            email = EmailMessage(
                subject, message, from_email, ['peng.jiang@nih.gov'], reply_to=[from_email]
                )
            
            try:
                email.send()
                    
            except BadHeaderError:
                return render(request, 'error.html', {'message': 'Invalid header', 'GOBACK': 5})
            
            return redirect('email_send_complete')
    
    return render(request, "email/email_send.html", {'form': form})


def EmailSendSuccessView(request):
    return render(request, 'email/email_send_complete.html')
