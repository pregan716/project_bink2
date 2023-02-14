# Generated by Django 4.1.3 on 2022-12-31 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0027_bettingmarketoutcometype'),
    ]

    operations = [
        migrations.AddField(
            model_name='bettingoutcome',
            name='betting_market_outcome_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='betting_outcomes', to='backend.bettingmarketoutcometype'),
        ),
    ]