from django.db import models

# Create your models here.
class Company(models.Model):
    company_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

class JobPosting(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    reward = models.IntegerField()
    content = models.TextField()
    skill = models.CharField(max_length=100)

class User(models.Model):
    name = models.CharField(max_length=100)
    jobposting = models.ForeignKey(JobPosting, on_delete=models.SET_NULL, null=True, blank=True)
