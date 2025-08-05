from django.contrib import admin
from .models import Quote

class QuoteAdmin(admin.ModelAdmin):
    list_display = ('text', 'source', 'weight', 'likes_count', 'dislikes_count', 'views', 'created_at')

    def likes_count(self, obj):
        return obj.reactions.filter(reaction='like').count()
    likes_count.short_description = 'Лайки'
    likes_count.admin_order_field = 'likes_count'  # если нужно сортировать по аннотации (о ней ниже)

    def dislikes_count(self, obj):
        return obj.reactions.filter(reaction='dislike').count()
    dislikes_count.short_description = 'Дизлайки'
    dislikes_count.admin_order_field = 'dislikes_count'

admin.site.register(Quote, QuoteAdmin)