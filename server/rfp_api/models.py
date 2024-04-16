import uuid

from django.db import models
from django.template.defaultfilters import truncatechars
from pgvector.django import VectorField

from .transformer import model

CHAR_LENGTH = 50


class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


class Answer(models.Model):
    text = models.TextField()
    owner_organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: " + truncatechars(self.text, CHAR_LENGTH)


class Question(models.Model):
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
    vector_embedding = VectorField(dimensions=768, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: " + truncatechars(self.text, CHAR_LENGTH)

    def save(self, *args, **kwargs):
        self.vector_embedding = model.encode(self.text)
        super(Question, self).save(*args, **kwargs)


class Ticket(models.Model):
    status_choices = (("Active", "Active"), ("Completed", "Completed"), ("Pending", "Pending"))
    ticket_number = models.UUIDField(default=uuid.uuid4)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(Organization, on_delete=models.DO_NOTHING, null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    accepted_date = models.DateTimeField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    ticket_status = models.CharField(max_length=15, choices=status_choices)
    answer_id = models.IntegerField(null=True, blank=True)
    question_id = models.IntegerField(null=True, blank=True)
    auto_generated = models.BooleanField(default=False)

    def __str__(self):
        return self.description
