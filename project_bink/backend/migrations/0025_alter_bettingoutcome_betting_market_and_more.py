# Generated by Django 4.1.3 on 2022-12-19 02:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0024_remove_bettingoutcome_betting_outcome_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bettingoutcome',
            name='betting_market',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='betting_outcomes', to='backend.bettingmarket'),
        ),
        migrations.AlterField(
            model_name='bettingoutcomepriceupdate',
            name='betting_outcome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='betting_outcome_updates', to='backend.bettingoutcome'),
        ),
        migrations.AlterField(
            model_name='bettingoutcomepriceupdate',
            name='previous_update',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.bettingoutcomepriceupdate'),
        ),
    ]
