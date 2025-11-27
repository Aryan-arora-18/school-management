from django.db import models
from django.contrib.auth.models import User

from django.db import migrations, models
from django.conf import settings

import uuid

class School(models.Model):
    sch_name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255, blank=True)
    principal = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="school_principal"
    )
    teachers = models.ManyToManyField(
        User, related_name="school_teaching_at", blank=True
    )
   
    def __str__(self):
        return self.sch_name
    
    
    class Meta:
        ordering = ["id"]

class Students(models.Model):
    user = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name="created_students"  
    )
    add_uid = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="added_students"
    )
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    age = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
    
    
    class Meta:
        ordering = ["id"]
    
    

class Role(models.Model):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("principle", "Principle"),
        ("teacher", "Teacher"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="role_profile")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name="role_users")

    def __str__(self):
        username = self.user.username if self.user else "UnknownUser"
        return f"{username} - {self.role or 'unassigned'}"

        
    class Meta:
        ordering = ["id"]





