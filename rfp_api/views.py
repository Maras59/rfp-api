from django.shortcuts import redirect, render

from .models import Answer, Question


def index_page_view(request):
    return render(request, "index.html")


def delete_question_page_view(request, iQuestionID):
    Question.objects.get(id=iQuestionID).delete()
    return redirect(list_questions_page_view)


def edit_question_page_view(request, iQuestionID):
    question = Question.objects.get(id=iQuestionID)

    if request.method == "POST":
        question.text = request.POST.get("question")
        question.answer = request.POST.get("answer")
        question.save()

        return redirect(list_questions_page_view)

    context = {"question": question}
    return render(request, "editQuestion.html", context)


def list_answers_page_view(request):
    data = Answer.objects.all()
    context = {"answers": data}
    return render(request, "answerList.html", context)


def list_questions_page_view(request):
    if request.method == "POST":
        new_question = Question()
        new_question.text = request.POST.get("question")
        new_question.answer = request.POST.get("answer")
        new_question.save()

    data = Question.objects.all()
    context = {"questions": data}
    return render(request, "questionList.html", context)


def addQuestionPageView(request):
    return render(request, "addQuestion.html")
