from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Book
from django.contrib.auth.models import User
from .models import Notification
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_abandoned_books():
    try:
        hour_ago = timezone.now() - timedelta(minutes=1)
        books_to_update = Book.objects.filter(last_updated__lte=hour_ago, status=Book.TRANSLATING)

        print(f"Found {books_to_update.count()} books to update.")

        reergard_user = get_reergard_user()

        for book in books_to_update:
            print(f"Processing book '{book.title}'")

            # Debugging: Print the current status of the book
            print("Current status:", book.status)

            # Debugging: Change the status and print the new status
            new_status = Book.ABANDONED
            print(f"Changing status to {new_status}")
            book.set_status(new_status)
            book.save()

            # Debugging: Print the new status after saving
            print("Updated status:", book.status)

            # Debugging: Print the user and time before update
            print("User before update:", book.user)
            print("Last updated before update:", book.last_updated)

            # Update user and last_updated
            book.user = reergard_user
            book.last_updated = timezone.now()
            book.save()

            # Debugging: Print the user and time after update
            print("User after update:", book.user)
            print("Last updated after update:", book.last_updated)

            # Debugging: Print a message after processing each book
            print(f"Book '{book.title}' processed successfully")

        print("Task check_abandoned_books finished")

    except Exception as e:
        print("An error occurred:", e)

@shared_task
def send_abandoned_notification(book_id):
    try:
        book = Book.objects.get(id=book_id)
        abandoned_threshold = timezone.now() - timedelta(minutes=1)
        if book.status == 'translating' and book.last_activity_date <= abandoned_threshold:
            # Вызвать метод для изменения статуса книги и даты статуса
            book.update_status_to_abandoned()
            # Отправить уведомление о переносе в статус "Покинуті"
            notification_message = f'Книга "{book.title}" будет перенесена в статус "Покинуті" через 7 дней бездействия.'
            Notification.objects.create(user=book.owner, message=notification_message)
    except Book.DoesNotExist:
        logger.error(f"Book with id {book_id} not found.")
        pass

def get_reergard_user():

    #  вернуть существующего пользователя
    user, created = User.objects.get_or_create(username='reergard_user')
    return user


@shared_task
def simple_debug_task():
    print("Simple debug task executed successfully")
