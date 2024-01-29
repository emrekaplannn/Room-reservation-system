# room_reservation/apps.py
from django.apps import AppConfig

class RoomReservationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'room_reservation'

    # def ready(self):
    #     from . import signals  # Relative import
