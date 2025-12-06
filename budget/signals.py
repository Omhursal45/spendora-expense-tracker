from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .insights import generate_insights

@receiver(user_logged_in)
def create_insights(sender, user, request, **kwargs):
    generate_insights(user)
