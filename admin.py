from django.contrib import admin
from .models import Book,
from .tasks import send_abandoned_notification


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    actions = ['send_abandoned_notification']
    list_display = ['title','title_en', 'author', 'get_tags', 'get_fandoms', 'get_country', 'get_genres']
    list_filter = ['author', 'tags', 'fandoms', 'country', 'genres']
    search_fields = ['title', 'author__name']


   
    def send_abandoned_notification(self, request, queryset):
        for book in queryset:
            send_abandoned_notification.delay(book.id)
        self.message_user(request, f"Уведомления отправлены для {queryset.count()} книг.")

    send_abandoned_notification.short_description = "Отправить уведомление о покинутой книге"

    actions = [send_abandoned_notification]


