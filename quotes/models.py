from django.db import models
from django.core.exceptions import ValidationError

class Quote(models.Model):
    """
    Модель цитаты для хранения текста, источника и статистики.

    Атрибуты:
        text (TextField): Текст цитаты. Уникально, чтобы исключить дубликаты.
        source (CharField): Название источника (фильм, книга и т.п.).
        weight (PositiveIntegerField): Вес цитаты, задаётся при добавлении. Чем выше, тем больше шанс выдачи.
        likes (IntegerField): Количество лайков для цитаты.
        dislikes (IntegerField): Количество дизлайков.
        views (IntegerField): Счётчик просмотров цитаты.
        created_at (DateTimeField): Дата и время создания записи.
        updated_at (DateTimeField): Дата и время последнего обновления записи.

    Ограничения:
        - Уникальность по тексту цитаты.
        - Не допускается более 3 цитат на один источник.
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
    likes = models.IntegerField(
        default=0,
        help_text="Количество лайков."
    )
    dislikes = models.IntegerField(
        default=0,
        help_text="Количество дизлайков."
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
        Проверяет бизнес-правила перед сохранением.

        Выбрасывает ValidationError, если у данного источника уже есть 3 и более цитат.
        """
        existing_quotes_count = Quote.objects.filter(source=self.source).exclude(pk=self.pk).count()
        if existing_quotes_count >= 3:
            raise ValidationError(f"Для источника '{self.source}' уже добавлено 3 цитаты, лишние нельзя добавлять.")

    def __str__(self):
        """
        Возвращает человекочитаемое представление цитаты.
        """
        return f'"{self.text[:50]}..." из {self.source}'
