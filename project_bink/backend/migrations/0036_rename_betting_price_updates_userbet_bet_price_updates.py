# Generated by Django 4.1.3 on 2023-02-03 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0035_userbet_betting_price_updates'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userbet',
            old_name='betting_price_updates',
            new_name='bet_price_updates',
        ),
    ]
