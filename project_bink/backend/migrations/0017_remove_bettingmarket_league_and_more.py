# Generated by Django 4.1.3 on 2022-12-15 03:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_bettingevent_league_bettingevent_sport'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bettingmarket',
            name='league',
        ),
        migrations.RemoveField(
            model_name='bettingmarket',
            name='sport',
        ),
    ]
