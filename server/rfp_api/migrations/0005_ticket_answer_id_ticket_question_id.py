# Generated by Django 5.0.3 on 2024-04-09 02:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rfp_api", "0004_remove_ticket_created_by_remove_ticket_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="answer_id",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ticket",
            name="question_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
