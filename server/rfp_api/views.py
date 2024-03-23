import csv
from io import TextIOWrapper

from django.db import ProgrammingError, connection
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView

from .forms import SqlForm, UploadCSVForm
from .models import Answer, Organization, Question


# TODO: Get context for pages
# Questions page -> add link, view this Q and view this answer, both link to admin page entry for object for modification
# Answers page -> add links, view this answers questions and view this answer
#                 view answer -> admin page entry,
#                 view questions -> render questions page with context of only questions that are annswer by this question
def index_page_view(request):
    return render(request, "index.html")


class ListAnswersView(APIView):
    def get(self, request):
        search_term = request.query_params.get("search", "")
        data = Answer.objects.filter(text__icontains=search_term)
        context = {"answers": data}
        return render(request, "answerList.html", context)


class ListQuestionsView(APIView):
    def get(self, request):
        search_term = request.query_params.get("search", "")
        data = []
        if answer_id := request.query_params.get("q"):  # TODO: add error handling for unknown answer
            answer = Answer.objects.get(id=answer_id)
            data = answer.question_set.filter(text__icontains=search_term)
        else:
            data = Question.objects.filter(text__icontains=search_term)
        context = {"questions": data}
        return render(request, "questionList.html", context)


class CSVUploadView(View):
    def get(self, request):
        if not Organization.objects.exists():
            Organization.objects.create(name="Default Organization")
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
            return render(
                request, "upload.html", {"form": form, "message": "CSV file has been uploaded", "tone": "success"}
            )
        else:
            return render(request, "upload.html", {"form": form, "message": "Form is not valid", "tone": "danger"})

def execute_sql(request):
    form = SqlForm()
    results = []
    columns = []
    error_message = ""
    sql = ""
    if request.method == "POST":
        form = SqlForm(request.POST)
        if form.is_valid():
            sql = form.cleaned_data["sqlInput"]
            # IMPORTANT: You should sanitize and validate the SQL here before executing it
            try:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()
            except ProgrammingError as e:
                error_message = f"Invalid SQL query: {e}"
    return render(request, "executeSql.html", {"form": form, "results": results, "columns": columns, "error_message": error_message, "sql": sql})