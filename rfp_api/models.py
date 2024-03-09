from django.db import models
from django.template.defaultfilters import truncatechars

CHAR_LENGTH = 50


class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # user = models.ForeignKey('User', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.description}"


class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Answer(models.Model):
    text = models.TextField()
    owner_organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return truncatechars(self.text, CHAR_LENGTH) + f" | ANSWER ID: {str(self.id)}"

    @property
    def short_description(self):
        return truncatechars(self.text, 35)


class Question(models.Model):
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return truncatechars(self.text, CHAR_LENGTH) + f" | QUESTION ID: {str(self.id)}"

    @property
    def short_description(self):
        return truncatechars(self.text, 35)
