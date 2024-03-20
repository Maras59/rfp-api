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

import rfp_api.inference as api
import rfp_api.views as views

urlpatterns = [
    path("", views.index_page_view, name="index"),
    path("admin/", admin.site.urls),
    path("inference/", api.Inference.as_view()),
    path("init/", api.Init.as_view()),
    path("answerList/", views.list_answers_page_view, name="answers"),
    path("questionList/", views.list_questions_page_view, name="questions"),
    path("addQuestion/", views.addQuestionPageView, name="questions"),
    # path("editQuestion/<int:iQuestionID", editQuestionPageView, name="editQuestion"),
    # path("deleteQuestion/<int:iQuestionID", deleteQuestionPageView, name="deleteQuestion"),
]
