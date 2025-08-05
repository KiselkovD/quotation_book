from django.shortcuts import render
from .utils import get_random_quote_weighted
from .models import Quote, QuoteReaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import uuid
from django.db.models import Count, Q


def random_quote_view(request):
    """Отобразить случайную цитату с подсчётом просмотров и реакций пользователя."""
    quote = get_random_quote_weighted()
    if quote:
        quote.views += 1
        quote.save(update_fields=['views'])

        user_id = request.COOKIES.get('user_id')
        user_reaction_obj = None
        if user_id:
            user_reaction_obj = QuoteReaction.objects.filter(quote=quote, user_identifier=user_id).first()
        user_reaction = user_reaction_obj.reaction if user_reaction_obj else None

        likes = quote.reactions.filter(reaction='like').count()
        dislikes = quote.reactions.filter(reaction='dislike').count()

        context = {
            'quote': quote,
            'likes': likes,
            'dislikes': dislikes,
            'user_reaction': user_reaction,
        }
    else:
        context = {'quote': None}

    response = render(request, 'quotes/random_quote.html', context)

    if not request.COOKIES.get('user_id'):
        response.set_cookie('user_id', str(uuid.uuid4()), max_age=365*24*60*60)

    return response


def top_quotes_view(request):
    """Отобразить топ 10 цитат с сортировкой по выбранному критерию."""
    sort = request.GET.get('sort', 'likes')

    qs = Quote.objects.annotate(
        likes_count=Count('reactions', filter=Q(reactions__reaction='like')),
        dislikes_count=Count('reactions', filter=Q(reactions__reaction='dislike'))
    )

    if sort == 'new':
        quotes = qs.order_by('-created_at')[:10]
    elif sort == 'views':
        quotes = qs.order_by('-views')[:10]
    elif sort == 'dislikes':
        quotes = qs.order_by('-dislikes_count')[:10]
    else:  # по умолчанию сортируем по лайкам
        quotes = qs.order_by('-likes_count')[:10]

    context = {
        'top_quotes': quotes,
        'current_sort': sort,
    }
    return render(request, 'quotes/top_quotes.html', context)


@require_POST
def react_quote(request, quote_id):
    """Обработать лайк или дизлайк пользователя с учётом cookie user_id."""
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
            obj.delete()  # снять реакцию
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
