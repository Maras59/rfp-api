from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _

from .models import Answer, Organization, Question


# Register your models here.
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    search_fields = ("id", "text")

    list_display = ("id", "text", "view_questions_link")
    readonly_fields = ("id",)

    def view_questions_link(self, obj):
        count = obj.question_set.count()
        url = reverse("admin:rfp_api_question_changelist") + "?" + urlencode({"answer__id": f"{obj.id}"})
        return format_html('<a href="{}">{} Question(s)</a>', url, count)

    view_questions_link.short_description = "Questions"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ("id", "text")
    list_display = ("id", "text", "view_answer_link")
    readonly_fields = ("id",)

    def view_answer_link(self, obj):
        if obj.answer:
            url = reverse("admin:rfp_api_answer_changelist") + "?" + urlencode({"id": f"{obj.answer.id}"})
            return format_html('<a href="{}">Answer</a>', url)
        else:
            return "NO ANSWER"

    view_answer_link.short_description = "Answer"


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
