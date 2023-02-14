# Generated by Django 4.1.3 on 2022-12-14 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_rename_last_updated_team_last_updated_utc_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='current_team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.team'),
        ),
    ]