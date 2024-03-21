import csv
from io import TextIOWrapper

from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView

from .forms import UploadCSVForm
from .models import Answer, Question, Organization


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


class CSVUploadView(View):
    def get(self, request):
        form = UploadCSVForm()
        return render(request, "upload.html", {"form": form})

    def post(self, request):
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = TextIOWrapper(request.FILES["csv_file"].file, encoding="utf-8")
            reader = csv.DictReader(csv_file)
            organization = Organization.objects.get(id=request.POST["organization"])
            for row in reader:
                question_text = row["question"]
                answer_text = row["answer"]
                print(f"question: {question_text}, answer: {answer_text}")
                answer = Answer.objects.create(text=answer_text, owner_organization=organization)
                Question.objects.create(text=question_text, answer=answer)
            return render(request, "upload.html", {"form": form, "message": "CSV file has been uploaded"})
        else:
            return render(request, "upload.html", {"form": form})
