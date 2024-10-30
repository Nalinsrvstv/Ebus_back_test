# utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def send_welcome_email(email, password,username):
    subject = 'Welcome to Your Website'
    from_email = 'nk@gmail.com'  # Replace with your email
    recipient_list = [email]

    # Construct the template path
    template_path = 'welcomeEmail.html'

    # Load the custom email template
    html_template = get_template(template_path)
    # Create a context with template variables
    context = {
        'email': email,
        'password': password,
        'username':username,
    }

    # Render the HTML content with the context
    html_content = html_template.render(context)

    # Send the welcome email
    msg = EmailMultiAlternatives(subject, html_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_password_reset_email(email, username,link):
        # Construct the template path
    template_path = 'resetPassword.html'
    try:
        subject = 'Reset your password'
        from_email = 'nk@gmail.com'  # Replace with your email
        recipient_list = [email]
        # Load the custom email template
        html_template = get_template(template_path)
        # Create a context with template variables
        context = {
            'email': email,
            'link': link,
            'username':username,
        }
        # Render the HTML content with the context
        html_content = html_template.render(context)
        # Send the welcome email
        msg = EmailMultiAlternatives(subject, html_content, from_email, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except (ConnectionError, Exception) as e:
        return f"Email sending failed: {str(e)}"
