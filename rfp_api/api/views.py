from django.shortcuts import render
from django.http import HttpResponse
from .. models import Answer

def listAnswersPageView(request):
    data = Answer.objects.all()
    context = {"answers": data}
    return render(request, "listanswers.html", context)

