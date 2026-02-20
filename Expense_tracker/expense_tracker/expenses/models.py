# expenses/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
<<<<<<< HEAD

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.FloatField()
    category = models.CharField(max_length=50, default="Uncategorized")
 # store category as string
=======


class Wallet(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallets_created")
    members = models.ManyToManyField(User, related_name="wallets")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    amount = models.FloatField()
    category = models.CharField(max_length=50, default="Uncategorized")
>>>>>>> 1da35822626378c190b037b04eb757b0426bd0bf
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

<<<<<<< HEAD
=======
from django.db import models
from django.contrib.auth.models import User

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    icon = models.CharField(max_length=50, default='bi-wallet2')

    def __str__(self):
        return f"{self.category} - {self.amount}"
>>>>>>> 1da35822626378c190b037b04eb757b0426bd0bf
