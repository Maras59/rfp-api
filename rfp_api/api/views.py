from django.shortcuts import render, redirect
from django.http import HttpResponse
from .. models import Answer, Question

def indexPageView(request):
    return render(request, 'index.html')

def deleteQuestionPageView(request, iQuestionID):
    Question.objects.get(id=iQuestionID).delete()
    return redirect(listQuestionsPageView)


def editQuestionPageView(request, iQuestionID):
    question = Question.objects.get(id=iQuestionID)

    if request.method == 'POST':
        question.text = request.POST.get("question")
        question.answer = request.POST.get("answer")
        question.save()

        return redirect(listQuestionsPageView)
    
    context = {
        "question": question
    }
    return render(request, 'editQuestion.html', context)


def listAnswersPageView(request):
    data = Answer.objects.all()
    context = {"answers": data}
    return render(request, "answerList.html", context)

def listQuestionsPageView(request):

    if request.method == 'POST':
        new_question = Question()
        new_question.text = request.POST.get('question')
        new_question.answer = request.POST.get('answer')
        new_question.save( )


    data = Question.objects.all()
    context = {"questions": data}
    return render(request, "questionList.html", context)

def addQuestionPageView(request):
    return render(request, "addQuestion.html")