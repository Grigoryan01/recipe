from django.contrib import admin
from .models import Recipe  # импорт модели

admin.site.register(Recipe)  # регистрация модели в админке
