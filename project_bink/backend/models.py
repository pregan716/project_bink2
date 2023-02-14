from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('BettingMarketOutcomeType', blank=True, related_name="watchers")
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=100.00)


class Sport(models.Model):
    sport_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.sport_name}"


class League(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
    league_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.sport.sport_name}-{self.league_name}"


class Team(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
    league = models.ForeignKey(League, on_delete=models.PROTECT)
    sd_team_key = models.CharField(max_length=100)
    sd_team_id = models.IntegerField()
    sd_global_team_id = models.IntegerField()
    sd_player_id = models.IntegerField()
    city = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    conference = models.CharField(max_length=100, null=True)
    division = models.CharField(max_length=100, null=True)
    full_name = models.CharField(max_length=100)
    stadium_id = models.IntegerField(null=True)
    primary_color = models.CharField(max_length=100, null=True)
    secondary_color = models.CharField(max_length=100, null=True)
    tertiary_color = models.CharField(max_length=100, null=True)
    quaternary_color = models.CharField(max_length=100, null=True)
    wiki_logo_url = models.URLField(null=True)
    wiki_wordmark_url = models.URLField(null=True)
    draftkings_name = models.CharField(max_length=100, null=True)
    draftkings_player_id = models.IntegerField(null=True)
    fanduel_name = models.CharField(max_length=100, null=True)
    fanduel_player_id = models.IntegerField(null=True)
    fantasydraft_name = models.CharField(max_length=100, null=True)
    fantasydraft_player_id = models.IntegerField(null=True)
    yahoo_name = models.CharField(max_length=100, null=True)
    yahoo_player_id = models.IntegerField(null=True)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.full_name}"


class Player(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT)
    league = models.ForeignKey(League, on_delete=models.PROTECT)
    current_team = models.ForeignKey(Team, on_delete=models.PROTECT, null=True)
    sd_player_id = models.IntegerField()
    number = models.IntegerField(null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    height = models.CharField(max_length=20, null=True)
    weight = models.IntegerField(null=True)
    birth_date = models.DateTimeField(null=True)
    experience = models.IntegerField(null=True)
    fantasy_position = models.CharField(max_length=20, null=True)
    is_active = models.BooleanField()
    position_category = models.CharField(max_length=20)
    full_name = models.CharField(max_length=100)
    age = models.IntegerField(null=True)
    short_name = models.CharField(max_length=100)
    current_status = models.CharField(max_length=100)
    fantasy_alarm_id = models.IntegerField(null=True)
    sport_radar_id = models.CharField(max_length=100, null=True)
    roto_world_id = models.IntegerField(null=True)
    roto_wire_id = models.IntegerField(null=True)
    stats_id = models.IntegerField(null=True)
    sports_direct_id = models.IntegerField(null=True)
    xml_id = models.IntegerField(null=True)
    fanduel_id = models.IntegerField(null=True)
    draftkings_id = models.IntegerField(null=True)
    yahoo_id = models.IntegerField(null=True)
    fanduel_name = models.CharField(max_length=100, null=True)
    draftkings_name = models.CharField(max_length=100, null=True)
    yahoo_name = models.CharField(max_length=100, null=True)
    fantasy_draft_id = models.IntegerField(null=True)
    fantasy_draft_name = models.CharField(max_length=100, null=True)
    usa_today_id = models.IntegerField(null=True)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.first_name}.{self.last_name}.{self.position}"


class Sportsbook(models.Model):
    sd_sportsbook_id = models.IntegerField()
    sportsbook_name  = models.CharField(max_length=100)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.sportsbook_name}"


class BetType(models.Model):
    data_provider = models.CharField(max_length=100)
    bet_type_id = models.IntegerField()
    bet_type_name = models.CharField(max_length=100)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.bet_type_name}"


class BettingMarketType(models.Model):
    data_provider = models.CharField(max_length=100)
    betting_market_type_id = models.IntegerField()
    betting_market_type_name = models.CharField(max_length=100)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.betting_market_type_name}"


class BettingPeriodType(models.Model):
    data_provider = models.CharField(max_length=100)
    betting_period_type_id = models.IntegerField()
    betting_period_type_name = models.CharField(max_length=100)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.betting_period_type_name}"


class BettingEventType(models.Model):
    data_provider = models.CharField(max_length=100)
    betting_event_type_id = models.IntegerField()
    betting_event_type_name = models.CharField(max_length=100)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.betting_event_type_name}"


class BettingOutcomeType(models.Model):
    data_provider = models.CharField(max_length=100)
    betting_outcome_type_id = models.IntegerField()
    betting_outcome_type_name = models.CharField(max_length=100)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.betting_outcome_type_name}"


class BettingResultType(models.Model):
    data_provider = models.CharField(max_length=100)
    betting_result_type_id = models.IntegerField()
    betting_result_type_name = models.CharField(max_length=100)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.betting_result_type_name}"


class ResultedMarket(models.Model):
    data_provider = models.CharField(max_length=100)
    betting_market_type = models.ForeignKey(BettingMarketType, on_delete=models.PROTECT)
    bet_type = models.ForeignKey(BetType, on_delete=models.PROTECT)
    betting_period_type =  models.ForeignKey(BettingPeriodType, on_delete=models.PROTECT)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.betting_market_type}-{self.bet_type}-{self.betting_period_type}"


class BettingEvent(models.Model):
    data_provider = models.CharField(max_length=100, default='sportsdata')
    betting_event_id = models.IntegerField(unique=True)
    betting_event_name = models.CharField(max_length=100)
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, related_name="betting_events", null=True)
    league = models.ForeignKey(League, on_delete=models.PROTECT, related_name="betting_events", null=True)
    betting_event_season = models.IntegerField()
    betting_event_type_id  = models.IntegerField()
    betting_event_type_name = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    created_datetime = models.DateTimeField()
    updated_datetime = models.DateTimeField()
    score_id = models.IntegerField(null=True)
    global_score_id = models.IntegerField(null=True)
    game_status = models.CharField(max_length=100, null=True)
    quarter = models.CharField(max_length=100, null=True)
    away_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="betting_event_away_team", null=True)
    home_team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="betting_event_home_team", null=True)
    away_team_score = models.IntegerField(null=True)
    home_team_score = models.IntegerField(null=True)
    total_score = models.IntegerField(null=True)
    game_start_datetime = models.DateTimeField(null=True)
    last_updated_utc = models.DateTimeField()
    last_markets_update_utc = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.betting_event_name}-{self.start_datetime}"


class BettingMarket(models.Model):
    data_provider = models.CharField(max_length=100, default='sportsdata')
    betting_market_id = models.IntegerField(unique=True)
    betting_market_name = models.CharField(max_length=100)
    betting_event = models.ForeignKey(BettingEvent, on_delete=models.PROTECT, related_name="betting_markets")
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, related_name="betting_markets", null=True)
    league = models.ForeignKey(League, on_delete=models.PROTECT, related_name="betting_markets", null=True)
    betting_market_type = models.ForeignKey(BettingMarketType, on_delete=models.PROTECT, related_name="betting_markets")
    bet_type = models.ForeignKey(BetType, on_delete=models.PROTECT, related_name="betting_markets")
    betting_period_type = models.ForeignKey(BettingPeriodType, on_delete=models.PROTECT, related_name="betting_markets")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, null=True, related_name="betting_markets")
    player = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, related_name="betting_markets")
    created_datetime = models.DateTimeField()
    updated_datetime = models.DateTimeField()
    is_bet_available = models.BooleanField()
    last_updated_utc = models.DateTimeField()
    result_update_datetime = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.betting_market_name}-{self.betting_event}-{self.bet_type}"

class BettingMarketOutcomeType(models.Model):
    market_outcome_type_combo = models.CharField(max_length=200, unique=True)
    betting_market = models.ForeignKey(BettingMarket, on_delete=models.CASCADE, related_name="betting_market_outcome_types")
    betting_outcome_type = models.ForeignKey(BettingOutcomeType, on_delete=models.PROTECT, related_name="betting_market_outcome_types")
    actual_value = models.DecimalField(max_digits=10, decimal_places=4, null=True)

    def __str__(self):
        return f"{self.market_outcome_type_combo}"


class Bet(models.Model):
    bet_identifier = models.CharField(max_length=100)
    betting_market_outcome_type = models.ForeignKey(BettingMarketOutcomeType, on_delete=models.CASCADE, related_name="bets", null=True)
    sportsbook = models.ForeignKey(Sportsbook, on_delete=models.PROTECT, related_name="bets")
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, related_name="betting_outcomes")
    league = models.ForeignKey(League, on_delete=models.PROTECT, related_name="betting_outcomes")
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="betting_outcomes", null=True)
    player = models.ForeignKey(Player, on_delete=models.PROTECT, related_name="betting_outcomes", null=True)
    participant = models.CharField(max_length=100, null=True)
    is_available = models.BooleanField()
    is_alternate = models.BooleanField()
    is_in_play = models.BooleanField()
    sportsbook_market_id = models.CharField(max_length=100, null=True)
    updated_datetime = models.DateTimeField()
    last_updated_utc = models.DateTimeField()
    def most_recent_price_update(self):
        return self.bet_price_updates.get(is_most_recent_update=True)
    def most_recent_value(self):
        return self.bet_price_updates.get(is_most_recent_update=True).value
    def most_recent_payout_american(self):
        return self.bet_price_updates.get(is_most_recent_update=True).payout_american
    
    def __str__(self):
        return f"{self.bet_identifier}"

class BetPriceUpdate(models.Model):
    data_provider = models.CharField(max_length=100, default='sportsdata')
    betting_outcome_id = models.IntegerField(unique=True)
    bet = models.ForeignKey(Bet, on_delete=models.PROTECT, related_name="bet_price_updates")
    payout_american = models.IntegerField()
    payout_decimal = models.DecimalField(max_digits=10, decimal_places=4)
    value = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    is_first_update = models.BooleanField()
    is_most_recent_update = models.BooleanField()
    previous_update = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    is_available = models.BooleanField()
    betting_result = models.ForeignKey(BettingResultType, on_delete=models.PROTECT, null=True)
    created_datetime = models.DateTimeField()
    updated_datetime = models.DateTimeField(null=True)
    unlisted_datetime = models.DateTimeField(null=True)
    result_update_datetime = models.DateTimeField(null=True)
    sportsbook_outcome_id = models.CharField(max_length=100, null=True)
    sportsbook_url = models.CharField(max_length=500, null=True)
    last_updated_utc = models.DateTimeField()

    def __str__(self):
        return f"{self.betting_outcome_id}"


class UserBet(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bets_placed')
    betting_market_outcome_type = models.ForeignKey(BettingMarketOutcomeType, on_delete=models.PROTECT, related_name='bets_placed')
    bet_price_updates = models.ManyToManyField(BetPriceUpdate, related_name='bets_placed')
    value = models.DecimalField(max_digits=10, decimal_places=4, null=True)
    wager_amount = models.DecimalField(max_digits=12, decimal_places=4)
    payout_american = models.IntegerField()
    placed_datetime = models.DateTimeField()
    is_win = models.BooleanField(null=True)
    result_update_datetime = models.DateTimeField(null=True)
    def market_outcome_type_value(self):
        return f'{self.betting_market_outcome_type.market_outcome_type_combo}-{self.value}'

    def __str__(self):
        return f"{self.id}"