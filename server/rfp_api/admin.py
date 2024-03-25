from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from .models import Answer, Organization, Question, Ticket


# Register your models here.
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    search_fields = ('id', 'text')

    list_display = ('id', 'text', 'view_questions_link')
    readonly_fields = ('id',)

    def view_questions_link(self, obj):
        count = obj.question_set.count()
        url = (
            reverse('admin:rfp_api_question_changelist')
            + '?'
            + urlencode({'answer__id': f'{obj.id}'})
        )
        return format_html('<a href="{}">{} Question(s)</a>', url, count)

    view_questions_link.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('id', 'text')
    list_display = ('id', 'text', 'view_answer_link')
    readonly_fields = ('id',)

    def view_answer_link(self, obj):
        if obj.answer:
            url = (
                reverse('admin:rfp_api_answer_changelist')
                + '?'
                + urlencode({'id': f'{obj.answer.id}'})
            )
            return format_html('<a href="{}">Answer</a>', url)
        else:
            return 'NO ANSWER'

    view_answer_link.short_description = 'Answer'


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('issue', 'question_link', 'answer_link', 'resolved')

    list_filter = ('resolved',)


    def question_link(self, obj):
        if obj.question_id and Question.objects.get(id=obj.question_id):
            url = reverse('admin:rfp_api_question_change', args=[obj.question_id])
            return format_html('<a href="{}">View Question</a>', url)
        else:
            return 'No Associated Question'
    
    def answer_link(self, obj):
        if obj.answer_id and Answer.objects.get(id=obj.answer_id):
            url = reverse('admin:rfp_api_answer_change', args=[obj.answer_id])
            return format_html('<a href="{}">View Answer</a>', url)
        else:
            return 'No Associated Answer'
