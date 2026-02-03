# expenses/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.FloatField()
    category = models.CharField(max_length=255)  # <-- just a simple text field
    date_created = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return self.title
