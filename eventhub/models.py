from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    class Role(models.TextChoices):
        CLIENT = "client", "Client"
        ADMIN = "admin", "Admin"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
    company_name = models.CharField(max_length=64)
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} ({self.role})"


class KBEntry(models.Model):
    class Category(models.TextChoices):
        DATABASE = "database", "Database"
        DJANGO = "django", "Django"
        FRAMEWORK = "framework", "Framework"
        GENERAL = "general", "General"

    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:50]


class QueryLog(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="query_logs")
    search_term = models.CharField(max_length=255)
    result_count = models.IntegerField(default=0)
    queried_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
