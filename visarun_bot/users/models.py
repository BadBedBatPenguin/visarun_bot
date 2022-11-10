from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models

CETINJE = 'Cetinje'
PODGORICA = 'Podgorica'
BUDVA = 'Budva'
BELGRAD = 'Belgrad'
FAST = 'fast'
SHOPPING = 'shopping'
TOURISM = 'tourism'
CITIES = [
    (CETINJE, 'Цетине'),
    (PODGORICA, 'Подгорица'),
    (BUDVA, 'Будва'),
    (BELGRAD, 'Белград'),
]
VISARUN_TYPES = [
    (FAST, 'Быстрая'),
    (SHOPPING, 'Покупки'),
    (TOURISM, 'Туризм'),
]
MIN_NUMBER_OF_PLACES = 'Общее количество мест не может быть меньше 0'
MAX_NUMBER_OF_PLACES_VALUE = 100
MAX_NUMBER_OF_PLACES = (
    f'Общее количество мест не может быть больше {MAX_NUMBER_OF_PLACES_VALUE}'
)


class User(AbstractUser):
    '''User model'''
    telegram_username = models.CharField(
        'Ник в телеграме',
        unique = True,
        max_length = 250,
    )
    city = models.CharField(
        'Город',
        blank = True,
        choices=CITIES,
        max_length=max(len(city) for _, city in CITIES),
    )
    date_joined = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return str(self.telegram_username)


class VisaRun(models.Model):
    '''Visarun model'''
    date = models.DateTimeField(
        'Дата поездки'
    )
    start_city = models.CharField(
        'Начальный город',
        blank = True,
        choices=CITIES,
        max_length=max(len(city) for city, _ in CITIES),
    )
    goal_city = models.CharField(
        'Конечный город',
        choices=CITIES,
        max_length=max(len(city) for city, _ in CITIES),
    )
    visarun_type = models.CharField(
        'Тип визарана',
        max_length=max(len(vsr_type) for vsr_type, _ in VISARUN_TYPES),
        choices=VISARUN_TYPES,
    )
    number_of_places = models.PositiveSmallIntegerField(
        'Количество мест',
        validators = (validators.MinValueValidator(
            1, message=MIN_NUMBER_OF_PLACES
        ), validators.MaxValueValidator(
            100, message=MAX_NUMBER_OF_PLACES
        ))
    )
    comment = models.TextField(
        'Комментарий',
        blank = True,
    )
    participants = models.ManyToManyField(
        to=User,
        verbose_name='Участники',
        related_name='visaruns',
    )

    class Meta:
        verbose_name = 'Визаран'
        verbose_name_plural = 'Визараны'
        ordering = ('-date',)

    def __str__(self) -> str:
        return f'Визаран из {self.start_city} назначенный на {self.date}'
