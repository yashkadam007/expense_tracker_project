from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

CATEGORY_CHOICES = (
    ('food', 'Food'),
    ('entertainment', 'Entertainment'),
    ('transportation', 'Transportation'),
    ('housing', 'Housing'),
    ('utilities', 'Utilities'),
    ('medical', 'Medical'),
    ('clothing', 'Clothing'),
    ('education', 'Education'),
    ('other', 'Other')
)


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.get_name_display()
    

class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.description
    
    def get_absolute_url(self):
        return reverse('expense-detail', kwargs={'pk': self.pk})
