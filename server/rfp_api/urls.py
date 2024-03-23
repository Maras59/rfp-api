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

from .inference import Inference
from .views import CSVUploadView, ListAnswersView, ListQuestionsView, execute_sql, index_page_view, download_csv

urlpatterns = [
    path("", index_page_view, name="index"),
    path("admin/", admin.site.urls),
    path("answerList/", ListAnswersView.as_view(), name="answers"),
    path("questionList/", ListQuestionsView.as_view(), name="questions"),
    path("inference/", Inference.as_view(), name="inference"),
    path("uploadCsv/", CSVUploadView.as_view(), name="upload-csv"),
    path("executeSql/", execute_sql, name="execute_sql"),
    path('download_csv/', download_csv, name='download_csv'),
]
