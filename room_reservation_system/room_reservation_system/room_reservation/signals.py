# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import ReservationSystem, ReservationSystemNotifications  # Import both classes


class ReservationSystemSignals:
    @staticmethod
    @receiver(post_save, sender=ReservationSystem.Room)
    def room_saved(sender, instance, created, **kwargs):
        ReservationSystemNotifications.notify(instance, "Room has been saved.")

    @staticmethod
    @receiver(post_delete, sender=ReservationSystem.Room)
    def room_deleted(sender, instance, **kwargs):
        ReservationSystemNotifications.notify(instance, "Room has been deleted.")

    @staticmethod
    @receiver(post_save, sender=ReservationSystem.Event)
    def event_saved(sender, instance, created, **kwargs):
        ReservationSystemNotifications.notify(instance, "Event has been saved.")

    @staticmethod
    @receiver(post_delete, sender=ReservationSystem.Event)
    def event_deleted(sender, instance, **kwargs):
        ReservationSystemNotifications.notify(instance, "Event has been deleted.")
