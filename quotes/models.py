from django.db import models
from django.core.exceptions import ValidationError


class Quote(models.Model):
    """
    Модель цитаты для хранения текста, источника и статистики.

    Атрибуты:
        text (TextField): Уникальный текст цитаты для исключения дублей.
        source (CharField): Название источника цитаты (фильм, книга и т.п.).
        weight (PositiveIntegerField): Вес цитаты для вероятностного выбора (чем выше — тем выше шанс выдачи).
        views (IntegerField): Счётчик просмотров цитаты.
        created_at (DateTimeField): Дата и время создания цитаты.
        updated_at (DateTimeField): Дата и время последнего обновления цитаты.

    Ограничения:
        - Уникальность текста цитаты.
        - Максимум 3 цитаты на один источник.
    """
    text = models.TextField(
        unique=True,
        help_text="Текст цитаты. Должен быть уникальным, без повторов."
    )
    source = models.CharField(
        max_length=200,
        help_text="Источник цитаты (например, название фильма или книги)."
    )
    weight = models.PositiveIntegerField(
        default=1,
        help_text="Вес цитаты для вероятностной выдачи (чем больше — тем выше шанс)."
    )
    views = models.IntegerField(
        default=0,
        help_text="Счётчик количества просмотров."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Дата и время создания цитаты."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Дата и время последнего обновления цитаты."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['text'], name='unique_quote_text'),
        ]
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"

    def clean(self):
        """
        Проверка бизнес-правил перед сохранением:
        Выбрасывает ValidationError, если у источника уже 3 и более цитат.
        """
        existing_quotes_count = Quote.objects.filter(source=self.source).exclude(pk=self.pk).count()
        if existing_quotes_count >= 3:
            raise ValidationError(f"Для источника '{self.source}' уже добавлено 3 цитаты, лишние нельзя добавлять.")

    def __str__(self):
        """
        Человекочитаемое представление цитаты: сокращённый текст и источник.
        """
        return f'"{self.text[:50]}..." из {self.source}'


class QuoteReaction(models.Model):
    """
    Модель реакции пользователя на цитату.

    Атрибуты:
        quote (ForeignKey): Связь с цитатой.
        user_identifier (CharField): Уникальный идентификатор пользователя (UUID из cookie).
        reaction (CharField): Тип реакции — "like" или "dislike".
        created_at (DateTimeField): Дата и время создания реакции.

    Ограничения:
        - Для одной цитаты и одного пользователя может быть только одна реакция.
    """
    quote = models.ForeignKey('Quote', on_delete=models.CASCADE, related_name='reactions')
    user_identifier = models.CharField(max_length=100)  # UUID из cookie
    reaction = models.CharField(max_length=7, choices=(('like', 'Like'), ('dislike', 'Dislike')))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('quote', 'user_identifier')

