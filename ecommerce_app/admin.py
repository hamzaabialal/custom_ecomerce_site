from django.contrib import admin
from .models import UserTemplate
# Register your models here.

# admin.py
from django.contrib import admin
from .models import UserTemplate
from django.db import models
from django.forms import Textarea

@admin.register(UserTemplate)
class UserTemplateAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 80})},
    }
