from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Insight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
