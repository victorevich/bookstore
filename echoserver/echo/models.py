from django.db import models
from django.contrib.auth.models import AbstractUser
class Books(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.title

    class Meta:
        db_table = 'books'
        managed = False


class User(AbstractUser):
    ROLES = (
        ('user', 'user'),
        ('admin', 'admin'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='user')
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    def __str__(self):
        return self.username

    class Meta:
        db_table = 'User'