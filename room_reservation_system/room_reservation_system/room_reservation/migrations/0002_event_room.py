# Generated by Django 4.2.7 on 2023-12-15 17:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('room_reservation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='room_reservation.room'),
        ),
    ]
