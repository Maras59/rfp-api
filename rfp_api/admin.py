from django.contrib import admin

from .models import Answer, Organization, Question, User

# Register your models here.
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'id')
    readonly_fields = ('id',)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'id')
    readonly_fields = ('id',)

admin.site.register(Organization)
admin.site.register(User)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Question, QuestionAdmin)
