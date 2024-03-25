from django.core.management.base import BaseCommand
from rfp_api.inference import collection
from rfp_api.models import Question


class Command(BaseCommand):
    help = "Check if all questions in PostgreSQL are represented in Milvus"

    def handle(self, *args, **options):
        existing_question_ids = collection.get_id_set()
        if not existing_question_ids:
            self.stdout.write(self.style.WARNING("No questions in milvus collection"))
        for question in Question.objects.all():
            if question.id in existing_question_ids:
                continue
            self.stdout.write(self.style.SUCCESS(f"Inserting question {question.id} into milvus collection"))
            collection.insert_question(question.id, question.text)
