from django.shortcuts import render
from .utils import get_random_quote_weighted
from .models import Quote

def random_quote_view(request):
    """
    Отображает страницу с одной случайной цитатой с учётом веса.
    """
    quote = get_random_quote_weighted()
    if quote:
        quote.views += 1
        quote.save(update_fields=['views'])
    
    return render(request, 'quotes/random_quote.html', {'quote': quote})

def top_quotes_view(request):
    """
    Отображает 10 самых популярных цитат, отсортированных по количеству лайков.
    """
    top_quotes = Quote.objects.order_by('-likes')[:10]
    return render(request, 'quotes/top_quotes.html', {'top_quotes': top_quotes})