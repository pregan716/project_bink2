# Generated by Django 4.1.3 on 2022-12-14 19:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0011_alter_bettingevent_quarter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bettingevent',
            name='away_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='betting_event_away_team', to='backend.team'),
        ),
        migrations.AlterField(
            model_name='bettingevent',
            name='home_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='betting_event_home_team', to='backend.team'),
        ),
    ]