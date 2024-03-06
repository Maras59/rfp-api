from django.contrib import admin

from .models import Answer, Organization, Question, User
import csv
from django.http import HttpResponse
from django.contrib import admin

# Register your models here.
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'id')
    readonly_fields = ('id',)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'id')
    readonly_fields = ('id',)

def export_to_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]  # Adapt to include specific fields

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response

export_to_csv.short_description = "Export Selected Questions to CSV"

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'is_active', 'answer', 'created_at']
    actions = [export_to_csv]

admin.site.register(Organization)
admin.site.register(User)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Question, QuestionAdmin)
