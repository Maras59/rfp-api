from django.contrib import admin
from .models import Organization, User, Answer, Question

# Register your models here.

admin.site.register(Organization)
admin.site.register(User)
admin.site.register(Answer)
admin.site.register(Question)