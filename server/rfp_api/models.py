from django.db import models
from django.template.defaultfilters import truncatechars

CHAR_LENGTH = 50


class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}, {self.description}"


class Answer(models.Model):
    text = models.TextField()
    owner_organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.id)} | " + truncatechars(self.text, CHAR_LENGTH)

    @property
    def short_description(self):
        return truncatechars(self.text, 35)


class Question(models.Model):
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.id)} | " + truncatechars(self.text, CHAR_LENGTH)

    @property
    def short_description(self):
        return truncatechars(self.text, 35)
