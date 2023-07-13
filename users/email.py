from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_request_download_mail(email, token):
    subject = 'eRepository Requests Granted'

    # Load the HTML template
    html_message = render_to_string('visitors/welcome.html', {'token': token})

    # Strip HTML tags to create a plain text version of the email
    plain_message = strip_tags(html_message)

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]

    # Create the EmailMultiAlternatives object and attach both HTML and plain text versions of the email
    email = EmailMultiAlternatives(subject, plain_message, email_from, recipient_list)
    email.attach_alternative(html_message, "text/html")

    # Send the email
    email.send()
    return True
