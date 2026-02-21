from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOISES =[
        ('manager','Manager'),
        ('customer','Customer')
    ]
    role =models.CharField(max_length=10 ,choices=ROLE_CHOISES ,default='customer')
    
    def __str__(self):
        return self.username