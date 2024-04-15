from collections import defaultdict

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.http import JsonResponse
from rest_framework.views import APIView
from source.milvus_index import MilvusConnectionSecrets, MilvusService

from .models import Answer, Organization, Question, Ticket

credentials = MilvusConnectionSecrets(user="username", password="password", host="standalone")
collection = MilvusService(credentials)


@receiver(pre_delete, sender=Question)
def on_question_delete(sender, instance, **kwargs):
    collection.drop_question(instance.id)


@receiver(pre_save, sender=Question)
def on_question_update(sender, instance, **kwargs):
    if instance.pk and not instance._state.adding:  # If the primary key exists and not adding a new instance
        collection.update_question(instance.id, instance.text)


@receiver(post_save, sender=Question)
def on_question_insert(sender, instance, created, **kwargs):
    if created:
        collection.insert_question(instance.id, instance.text)


class Inference(APIView):
    def post(self, request) -> JsonResponse:
        """
        The endpoint to handle POST requests and return JsonResponse with answers to similar questions.
        This is the main API endpoint. All questions will be embedded and then compared with embeddings in Milvus

        Parameters:
            request: HttpRequest object containing the payload data

        Returns:
            JsonResponse: JSON response with answers to similar questions
        """
        payload = request.data
        if not (question := payload.get("question")):
            return JsonResponse({"res": "No question found in the payload"})

        return_count = int(payload.get("count", 2))
        threshold = float(payload.get("threshold", 0.4))

        query_results = collection.search(question, k=10, threshold=threshold)

        # get nearest neighbor
        classes = defaultdict(int)
        answer_metadata = defaultdict(lambda: (0, 0))
        for item in query_results:
            question = Question.objects.get(id=item.question_id)
            classes[question.answer.id] += item.score
            _, score = answer_metadata[question.answer.id]
            if score < item.score:
                answer_metadata[question.answer.id] = (question.id, item.score)

        # create list of tuples (score, class) and sort it
        sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
        answer_ids = sorted_classes[:return_count]

        answers = []
        for answer_id, score in answer_ids:
            answer = Answer.objects.get(id=answer_id)
            question_id, _ = answer_metadata[answer_id]
            question = Question.objects.get(id=question_id)
            answers.append(
                {"similar_question": question.text, "answer": answer.text, "score": score, "answer_id": answer.id}
            )

        if not answers:
            Ticket(description=payload.get("question"), ticket_status="Pending", auto_generated=True).save()

        return JsonResponse(answers, safe=False)


class InsertQuestion(APIView):
    def post(self, request):
        """
        Function to handle POST requests. Creates a new question based on the provided data in the request.
        :param request: The HTTP request object containing data for creating a new question.
        :return: A JSON response with the ID of the newly created question if successful, otherwise an error message.
        """
        payload = request.data
        question_text = payload.get("question_text")

        if Question.objects.filter(text=question_text).exists():
            return JsonResponse({"error": "Question already exists in the database"})

        answer_id = payload.get("answer_id")

        try:
            answer = Answer.objects.get(id=answer_id)
            question = Question.objects.create(text=question_text, answer=answer)
            question.save()
        except Exception as e:
            return JsonResponse({"error": str(e)})

        return JsonResponse({"id": question.id})


class SendTicket(APIView):
    def post(self, request):
        """
        Function to handle POST requests. Creates a new ticket based on the provided data in the request.
        :param request: The HTTP request object containing data for creating a new ticket.
        :return: A JSON response with the ID of the newly created ticket if successful, otherwise an error message.
        """
        payload = request.data

        description = payload.get("description")
        assigned_to_name = payload.get("assigned_to")
        answer_id = payload.get("answer_id")
        question_id = payload.get("question_id")

        assigned_org = Organization.objects.filter(name=assigned_to_name).first()
        if not assigned_org:
            assigned_org = None

        try:
            ticket = Ticket.objects.create(
                description=description,
                assigned_to=assigned_org,
                question_id=question_id,
                answer_id=answer_id,
                ticket_status="Pending",
            )
            ticket.save()

        except Exception as e:
            return JsonResponse({"error": str(e)})
        return JsonResponse({"id": ticket.id})
