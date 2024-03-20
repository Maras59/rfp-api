"""
URL configuration for rfp_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from .inference import Inference, Init
from .views import addQuestionPageView, index_page_view, list_answers_page_view, list_questions_page_view

urlpatterns = [
    path("", index_page_view, name="index"),
    path("admin/", admin.site.urls),
    path("inference/", Inference.as_view()),
    path("init/", Init.as_view()),
    path("answerList/", list_answers_page_view, name="answers"),
    path("questionList/", list_questions_page_view, name="questions"),
    path("addQuestion/", addQuestionPageView, name="questions"),
    # path("editQuestion/<int:iQuestionID", editQuestionPageView, name="editQuestion"),
    # path("deleteQuestion/<int:iQuestionID", deleteQuestionPageView, name="deleteQuestion"),
]
