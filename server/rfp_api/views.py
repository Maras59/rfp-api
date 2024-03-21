from django.shortcuts import render
from rest_framework.views import APIView

from .models import Answer, Question


# TODO: Get context for pages
# Questions page -> add link, view this Q and view this answer, both link to admin page entry for object for modification
# Answers page -> add links, view this answers questions and view this answer
#                 view answer -> admin page entry,
#                 view questions -> render questions page with context of only questions that are annswer by this question
def index_page_view(request):
    return render(request, "index.html")


class ListAnswersView(APIView):
    def get(self, request):
        data = Answer.objects.all()
        context = {"answers": data}
        return render(request, "answerList.html", context)


class ListQuestionsView(APIView):
    def get(self, request):
        data = []
        if answer_id := request.query_params.get("q"):  # TODO: add error handling for unknown answer
            answer = Answer.objects.get(id=answer_id)
            data = answer.question_set.all()
        else:
            data = Question.objects.all()
        context = {"questions": data}
        return render(request, "questionList.html", context)
