from django.urls import path

from .views import EmailSendView, EmailSendSuccessView

urlpatterns = [
    path('email_send/', EmailSendView, name='email_send'),
    path('email_send_complete/', EmailSendSuccessView, name='email_send_complete'),
    ]
