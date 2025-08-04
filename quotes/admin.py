from django.contrib import admin
from .models import Quote

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    # Поля, которые отображаются в списке объектов в админке
    list_display = ('text', 'source', 'weight', 'likes', 'dislikes', 'views')
    # Поля, по которым осуществляется поиск
    search_fields = ('text', 'source')
