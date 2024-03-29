import csv
from datetime import datetime
from io import TextIOWrapper

from django.db import ProgrammingError, connection
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView

from .forms import SqlForm, UploadCSVForm
from .models import Answer, Organization, Question


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
                # Sanitize SQL by removing any potentially harmful characters
                sanitized_sql = sql.strip()

                with connection.cursor() as cursor:
                    cursor.execute(sanitized_sql)
                    if cursor.description is not None:
                        columns = [col[0] for col in cursor.description]
                        results = cursor.fetchall()
                results = [
                    [cell.isoformat() if isinstance(cell, datetime) else cell for cell in row] for row in results
                ]
                request.session["results"] = results
                request.session["columns"] = columns
            except ProgrammingError as e:
                error_message = f"Invalid SQL query: {e}"
    return render(
        request,
        "executeSql.html",
        {"form": form, "results": results, "columns": columns, "error_message": error_message, "sql": sql},
    )


def download_csv(request):
    # Get the results from the session
    results = request.session.get("results", [])
    columns = request.session.get("columns", [])

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="results.csv"'

    writer = csv.writer(response)
    writer.writerow(columns)
    for row in results:
        writer.writerow(row)

    return response
