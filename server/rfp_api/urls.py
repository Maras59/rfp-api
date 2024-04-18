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

from .endpoints import Inference, InsertQuestion, SendTicket
from .views import index_page_view, CSVUploadView, execute_sql, download_csv, ticket_details, all_tickets

urlpatterns = [
    path("", index_page_view, name="index"),
    path("accounts/login/", admin.site.login, name="login"),
    path("accounts/logout/", admin.site.logout, name="logout"),
    path("admin/", admin.site.urls),
    path("inference/", Inference.as_view(), name="inference"),
    path("insert_question/", InsertQuestion.as_view(), name="insert_question"),
    path("uploadCsv/", CSVUploadView.as_view(), name="upload-csv"),
    path("executeSql/", execute_sql, name="execute_sql"),
    path("download_csv/", download_csv, name="download_csv"),
    path("ticket-details/<int:pk>/", ticket_details, name="ticket-details"),
    path("send-ticket/", SendTicket.as_view(), name="send-ticket"),
    path("all-tickets/", all_tickets, name="all-tickets"),
]
