import random
from .models import Quote

def get_random_quote_weighted():
    """
    Возвращает случайную цитату из базы с учётом веса каждой цитаты.

    Логика:
    - Выбирает одну цитату с вероятностью, пропорциональной полю weight.
    """
    quotes = list(Quote.objects.all())
    if not quotes:
        return None  # Если цитат нет — вернуть None

    weights = [quote.weight for quote in quotes]
    selected_quote = random.choices(quotes, weights=weights, k=1)[0]
    return selected_quote
