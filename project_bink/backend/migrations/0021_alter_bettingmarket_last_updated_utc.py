# Generated by Django 4.1.3 on 2022-12-15 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0020_bettingevent_last_markets_update_utc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bettingmarket',
            name='last_updated_utc',
            field=models.DateTimeField(),
        ),
    ]
