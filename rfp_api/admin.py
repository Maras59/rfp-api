from django.contrib import admin

from .models import Answer, Organization, Question, User


# Register your models here.
@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("text", "id")
    readonly_fields = ("id",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "answer")
    readonly_fields = ("id",)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name")
