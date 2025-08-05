from django.shortcuts import render
from .utils import get_random_quote_weighted
from .models import Quote, QuoteReaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import uuid

def random_quote_view(request):
    quote = get_random_quote_weighted()
    if quote:
        quote.views += 1
        quote.save(update_fields=['views'])

        # Получаем user_id из cookie или None
        user_id = request.COOKIES.get('user_id')

        # Получаем текущую реакцию, если есть
        user_reaction_obj = None
        if user_id:
            user_reaction_obj = QuoteReaction.objects.filter(quote=quote, user_identifier=user_id).first()
        user_reaction = user_reaction_obj.reaction if user_reaction_obj else None

        context = {
            'quote': quote,
            'likes': quote.reactions.filter(reaction='like').count(),
            'dislikes': quote.reactions.filter(reaction='dislike').count(),
            'user_reaction': user_reaction,
        }
    else:
        context = {'quote': None}

    response = render(request, 'quotes/random_quote.html', context)

    # При отсутствии user_id в cookie создаём новый
    if not request.COOKIES.get('user_id'):
        response.set_cookie('user_id', str(uuid.uuid4()), max_age=365*24*60*60)

    return response

@require_POST

def top_quotes_view(request):
    """
    Отображает 10 самых популярных цитат, отсортированных по количеству лайков.
    """
    top_quotes = Quote.objects.order_by('-likes')[:10]
    return render(request, 'quotes/top_quotes.html', {'top_quotes': top_quotes})

def react_quote(request, quote_id):
    user_id = request.COOKIES.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())

    reaction_type = request.POST.get('reaction')
    if reaction_type not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid reaction'}, status=400)

    try:
        quote = Quote.objects.get(id=quote_id)
    except Quote.DoesNotExist:
        return JsonResponse({'error': 'Quote not found'}, status=404)

    obj, created = QuoteReaction.objects.get_or_create(
        quote=quote,
        user_identifier=user_id,
        defaults={'reaction': reaction_type}
    )

    if not created:
        if obj.reaction == reaction_type:
            obj.delete()
        else:
            obj.reaction = reaction_type
            obj.save()

    likes = quote.reactions.filter(reaction='like').count()
    dislikes = quote.reactions.filter(reaction='dislike').count()

    user_reaction_obj = QuoteReaction.objects.filter(quote=quote, user_identifier=user_id).first()
    user_reaction = user_reaction_obj.reaction if user_reaction_obj else None

    response = JsonResponse({'likes': likes, 'dislikes': dislikes, 'user_reaction': user_reaction})

    if 'user_id' not in request.COOKIES:
        response.set_cookie('user_id', user_id, max_age=365*24*60*60)

    return response
