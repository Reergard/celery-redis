import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.core.files import File
from django.urls import reverse
from django.contrib.auth.models import User
from slugify import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from ckeditor.fields import RichTextField
from django.utils import timezone
from celery import shared_task
from datetime import timedelta
from haystack import signals















class Book(models.Model):
    TRANSLATING = 'Перекладається'
    COMPLETED = 'Завершено'
    WAITING = 'Очікування нових розділів'
    ABANDONED = 'Покинутий'
    PAUSE = 'Перерва'

    STATUS_CHOICES = [
        (TRANSLATING, 'Перекладається'),
        (COMPLETED, 'Завершено'),
        (WAITING, 'Очікування нових розділів'),
        (ABANDONED, 'Покинутий'),
        (PAUSE, 'Перерва'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET(get_reergard_user), related_name='books')
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, null=True)
    author = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag)
    genres = models.ManyToManyField(Genres)
    fandoms = models.ManyToManyField(Fandom)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to=book_directory_path, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    viewed_by = models.ManyToManyField(User, blank=True, related_name="viewed_books")  # Связь "многие ко многим" с моделью User, позволяет отслеживать, кто из пользователей просмотрел книгу.
    pub_date = models.DateField(verbose_name='Дата створення', default=timezone.now) # Дата створення
    last_updated = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='books/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=TRANSLATING)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            num = 2
            while Book.objects.filter(slug=self.slug).exists():
                self.slug = "{}-{}".format(slugify(self.title), num)
                num += 1

        if not self.image:
            no_image_path = os.path.join(settings.STATICFILES_DIRS[0], 'catalog/image/no_image.png')
            self.image.save('no_image.png', File(open(no_image_path, 'rb')))



        if self.pk:
            previous_image = Book.objects.get(pk=self.pk).image
            if self.image != previous_image:
                if previous_image:
                    previous_image_path = os.path.join(settings.MEDIA_ROOT, str(previous_image))
                    if os.path.exists(previous_image_path):
                        os.remove(previous_image_path)



        if self.status == Book.ABANDONED:                                                          #через tasks
            self.last_updated = timezone.now()

        super().save(*args, **kwargs)


    def avg_rating(self):
        avg = self.book_ratings.all().aggregate(Avg('stars'))
        return round(avg.get('stars__avg') or 0, 2)

    @property
    def chapters_count(self):                       # количество глав
        return self.book_chapters.count()

    def is_adult(self):
        return self.is_adult  # Возвращаем значение поля is_adult



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message







