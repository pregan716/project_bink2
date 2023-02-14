# Generated by Django 4.1.3 on 2023-01-03 19:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0028_bettingoutcome_betting_market_outcome_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bet_identifier', models.CharField(max_length=100)),
                ('participant', models.CharField(max_length=100, null=True)),
                ('is_available', models.BooleanField()),
                ('is_alternate', models.BooleanField()),
                ('is_in_play', models.BooleanField()),
                ('sportsbook_market_id', models.CharField(max_length=100, null=True)),
                ('updated_datetime', models.DateTimeField()),
                ('last_updated_utc', models.DateTimeField()),
                ('betting_market_outcome_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bets', to='backend.bettingmarketoutcometype')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='betting_outcomes', to='backend.league')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='betting_outcomes', to='backend.player')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='betting_outcomes', to='backend.sport')),
                ('sportsbook', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bets', to='backend.sportsbook')),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='betting_outcomes', to='backend.team')),
            ],
        ),
        migrations.CreateModel(
            name='BetPriceUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_provider', models.CharField(default='sportsdata', max_length=100)),
                ('betting_outcome_id', models.IntegerField(unique=True)),
                ('payout_american', models.IntegerField()),
                ('payout_decimal', models.DecimalField(decimal_places=4, max_digits=10)),
                ('value', models.DecimalField(decimal_places=4, max_digits=10, null=True)),
                ('is_first_update', models.BooleanField()),
                ('is_most_recent_update', models.BooleanField()),
                ('is_available', models.BooleanField()),
                ('created_datetime', models.DateTimeField()),
                ('updated_datetime', models.DateTimeField(null=True)),
                ('unlisted_datetime', models.DateTimeField(null=True)),
                ('sportsbook_outcome_id', models.CharField(max_length=100, null=True)),
                ('sportsbook_url', models.CharField(max_length=500, null=True)),
                ('last_updated_utc', models.DateTimeField()),
                ('bet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bet_price_updates', to='backend.bet')),
                ('previous_update', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.betpriceupdate')),
            ],
        ),
        migrations.RemoveField(
            model_name='bettingoutcomepriceupdate',
            name='betting_outcome',
        ),
        migrations.RemoveField(
            model_name='bettingoutcomepriceupdate',
            name='previous_update',
        ),
        migrations.DeleteModel(
            name='BettingOutcome',
        ),
        migrations.DeleteModel(
            name='BettingOutcomePriceUpdate',
        ),
    ]
