# Generated by Django 4.2.7 on 2023-12-15 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(max_length=200)),
                ('capacity', models.IntegerField()),
                ('duration', models.IntegerField()),
                ('weekly', models.DateTimeField(blank=True, null=True)),
                ('permissions', models.JSONField(default=dict)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('map_image', models.CharField(blank=True, max_length=255, null=True)),
                ('permissions', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('capacity', models.IntegerField()),
                ('working_hours_start', models.DateTimeField()),
                ('working_hours_end', models.DateTimeField()),
                ('permissions', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
