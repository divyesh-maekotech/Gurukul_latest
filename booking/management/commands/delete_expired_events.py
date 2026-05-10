from django.core.management.base import BaseCommand

from booking.models import DailyEvent

class Command(BaseCommand):
    help = 'Delete expired daily events'

    def handle(self, *args, **kwargs):
        count = DailyEvent.delete_expired_events()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} expired events'))