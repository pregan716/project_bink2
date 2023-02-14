# Generated by Django 4.1.3 on 2022-12-15 02:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_alter_bettingevent_away_team_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BettingMarket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('betting_market_id', models.IntegerField()),
                ('betting_market_name', models.CharField(max_length=100)),
                ('created_datetime', models.DateTimeField()),
                ('updated_datetime', models.DateTimeField()),
                ('bets_available', models.BooleanField()),
                ('last_updated_utc', models.BooleanField()),
                ('bet_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='betting_markets', to='backend.bettype')),
                ('betting_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='betting_markets', to='backend.bettingevent')),
                ('betting_market_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='betting_markets', to='backend.bettingmarkettype')),
                ('betting_period_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='betting_markets', to='backend.bettingperiodtype')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='betting_markets', to='backend.league')),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='betting_markets', to='backend.player')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='betting_markets', to='backend.sport')),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='betting_markets', to='backend.team')),
            ],
        ),
    ]