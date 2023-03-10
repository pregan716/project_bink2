# Generated by Django 4.1.3 on 2022-12-15 03:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_remove_bettingevent_league_remove_bettingevent_sport'),
    ]

    operations = [
        migrations.AddField(
            model_name='bettingevent',
            name='league',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='betting_events', to='backend.league'),
        ),
        migrations.AddField(
            model_name='bettingevent',
            name='sport',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='betting_events', to='backend.sport'),
        ),
    ]
