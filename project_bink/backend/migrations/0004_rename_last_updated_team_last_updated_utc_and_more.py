# Generated by Django 4.1.3 on 2022-12-14 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_alter_team_stadium_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='last_updated',
            new_name='last_updated_utc',
        ),
        migrations.RenameField(
            model_name='team',
            old_name='sd_key',
            new_name='sd_team_key',
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sd_player_id', models.IntegerField()),
                ('number', models.IntegerField()),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('position', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=20)),
                ('height', models.CharField(max_length=20)),
                ('weight', models.IntegerField()),
                ('birth_date', models.DateField()),
                ('experience', models.IntegerField()),
                ('fantasy_position', models.CharField(max_length=20)),
                ('active', models.BooleanField()),
                ('position_category', models.CharField(max_length=20)),
                ('full_name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('short_name', models.CharField(max_length=100)),
                ('current_status', models.CharField(max_length=100)),
                ('fantasy_alarm_id', models.IntegerField()),
                ('sport_radar_id', models.CharField(max_length=100)),
                ('roto_world_id', models.IntegerField()),
                ('roto_wire_id', models.IntegerField()),
                ('stats_id', models.IntegerField()),
                ('sports_direct_id', models.IntegerField()),
                ('xml_id', models.IntegerField()),
                ('fanduel_id', models.IntegerField()),
                ('draftkings_id', models.IntegerField()),
                ('yahoo_id', models.IntegerField()),
                ('fanduel_name', models.CharField(max_length=100)),
                ('draftkings_name', models.CharField(max_length=100)),
                ('yahoo_name', models.CharField(max_length=100)),
                ('fantasy_draft_id', models.IntegerField()),
                ('fantasy_draft_name', models.CharField(max_length=100)),
                ('usa_today_id', models.IntegerField()),
                ('last_updated_utc', models.DateTimeField()),
                ('current_team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='backend.team')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='backend.league')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='backend.sport')),
            ],
        ),
    ]