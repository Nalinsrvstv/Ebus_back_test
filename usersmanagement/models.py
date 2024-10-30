from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email



class CustomPermissions(models.Model):
    
    class Meta:
        permissions = [
            ("create_project","Can create new project"),
            ("view_project","Can view project created")
        ]


