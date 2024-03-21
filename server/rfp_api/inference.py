from collections import defaultdict

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.http import JsonResponse
from rest_framework.views import APIView
from source.milvus_index import MilvusConnectionSecrets, MilvusService

from .models import Answer, Question

credentials = MilvusConnectionSecrets(user="username", password="password", host="standalone")
index = MilvusService(credentials)


@receiver(pre_delete, sender=Question)
def on_question_delete(sender, instance, **kwargs):
    index.drop_question(instance.id)


@receiver(pre_save, sender=Question)
def on_question_update(sender, instance, **kwargs):
    if instance.pk and not instance._state.adding:  # If the primary key exists and not adding a new instance
        index.update_question(instance.id, instance.text)


@receiver(post_save, sender=Question)
def on_question_insert(sender, instance, created, **kwargs):
    if created:
        index.insert_question(instance.id, instance.text)


class Inference(APIView):
    def post(self, request) -> JsonResponse:
        payload = request.data
        if not (question := payload.get("question")):
            return JsonResponse({"res": "No question found in the payload"})

        return_count = int(payload.get("count", 2))
        threshold = float(payload.get("threshold", 0.4))

        query_results = index.search(question, k=10, threshold=threshold)

        # get nearest neighbor
        classes = defaultdict(int)
        for item in query_results:
            question = Question.objects.get(id=item.question_id)
            classes[question.answer.id] += item.score

        # create list of tuples (score, class) and sort it
        sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
        question_ids = sorted_classes[:return_count]

        answers = []
        for question_id, score in question_ids:
            answer = Answer.objects.get(id=question_id)
            question = Question.objects.get(answer=answer)
            answers.append({"similar_question": question.text, "answer": answer.text, "score": score})

        return JsonResponse(answers, safe=False)
