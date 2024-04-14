import csv
from datetime import datetime
from io import TextIOWrapper

from django.contrib import messages
from django.db import ProgrammingError, connection
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from .forms import CreateTicketForm, SqlForm, UploadCSVForm
from .models import Answer, Organization, Question, Ticket


def index_page_view(request):
    return render(request, "index.html")


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


def create_ticket(request):
    if request.method == "POST":
        form = CreateTicketForm(request.POST)
        if form.is_valid():
            var = form.save(commit=False)
            var.created_by = request.organization
            var.ticket_status = "Pending"
            var.save()
            messages.info(request, "Your ticket has been successfully submitted.")
            return redirect("index")
        else:
            messages.warning(request, "Something went wrong. Please check form input")
            return redirect("create-ticket")
    else:
        form = CreateTicketForm()
        context = {"form": form}
        return render(request, "create_ticket.html", context)


def all_tickets(request):
    tickets = Ticket.objects.all()
    context = {"tickets": tickets}
    return render(request, "all_tickets.html", context)


def ticket_details(request, pk):
    ticket = Ticket.objects.get(pk=pk)
    context = {"ticket": ticket}
    return render(request, "ticket_details.html", context)


# def ticket_queue(request):
#    tickets = Ticket.objects.filter(ticket_status='Pending')
#    context = {'tickets':tickets}
#    return render(request, 'ticket_queue.html', context)

# def accept_ticket(request, pk):
#    ticket = Ticket.objects.get(pk=pk)
#    ticket.assigned_to = request.user
#    ticket.ticket_status = 'Active'
#    ticket.accepted_date = datetime.datetime.Now()
#    ticket.save()
#    messages.info(request, 'Ticket has been accepted. Please resolve as soon as possible!')
#    return redirect('ticket-queue')


# def close_ticket(request, pk):
#    ticket = Ticket.objects.get(pk=pk)
#    ticket.ticket_status = 'Completed'
#    ticket.is_resolved = True
#    ticket.closed_date = datetime.datetime.Now()
#    ticket.save()
#    messages.info(request, 'Ticket has been resolved.')
#    return redirect('ticket-queue')

# def workspace(request):
#    tickets = Ticket.objects.filter(assigned_to=request.organization, is_resolved=False)
#    context = {'tickets':tickets}
#    return render(request, 'workspace.html', context)

# def all_closed_tickets(request):
#    tickets = Ticket.objects.filter(assigned_to=request.organization, is_resolved=True)
#    context = {'tickets':tickets}
#    return render(request, 'all_closed_tickets.html', context)

# def update_ticket(request, pk):
#    ticket = Ticket.objects.get(pk=pk)
#    if request.method == 'POST':
#        form = UpdateTicketForm(request.POST, instance=ticket)
#        if form.is_valid():
#            form.save()
#            messages.info(request, 'Your ticket info has been updated and all the changes are saved in the Database')
#            return redirect('index.html')
#        else:
#            messages.warning(request, 'Something went wrong. Please check form input')
# return redirect('create-ticket')
#    else:
#        form = UpdateTicketForm(instance=ticket)
#        context = {'form':form}
#        return render(request, 'update_ticket.html', context)
