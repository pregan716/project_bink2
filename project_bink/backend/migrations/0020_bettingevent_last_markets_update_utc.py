# Generated by Django 4.1.3 on 2022-12-15 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_bettingevent_league_bettingevent_sport'),
    ]

    operations = [
        migrations.AddField(
            model_name='bettingevent',
            name='last_markets_update_utc',
            field=models.DateTimeField(null=True),
        ),
    ]
