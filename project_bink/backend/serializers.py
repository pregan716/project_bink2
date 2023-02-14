# import serializer from rest_framework
from rest_framework import serializers
 
# import model from models.py
from .models import BettingMarket, BettingMarketOutcomeType, BettingEvent, Player, Team, Bet, User, UserBet


class BetSerializer(serializers.ModelSerializer):
    sportsbook = serializers.SlugRelatedField(slug_field='sportsbook_name', read_only=True)
    most_recent_price_update = serializers.SlugRelatedField(slug_field='betting_outcome_id', read_only=True)

    class Meta:
        model = Bet
        fields = ('sportsbook', 'most_recent_value', 'most_recent_payout_american', 'most_recent_price_update', 'bet_identifier')

class TeamSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Team
        fields = ('sd_team_key')


class BettingEventSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BettingEvent
        fields = ('betting_event_name', 'start_datetime')


class PlayerSerializer(serializers.ModelSerializer):
    current_team = serializers.SlugRelatedField(slug_field='sd_team_key', read_only=True)

    class Meta:
        model = Player
        fields = ('full_name', 'position', 'current_team')


class OddsFeedBettingMarketOutcomeTypeSerializer(serializers.ModelSerializer):
    betting_outcome_type = serializers.SlugRelatedField(slug_field='betting_outcome_type_name', read_only=True)
    bets = BetSerializer(many=True, read_only=True)
    
    class Meta:
        model = BettingMarketOutcomeType
        fields = ('id', 'betting_outcome_type', 'bets')


class OddsFeedBettingMarketSerializer(serializers.ModelSerializer):
    betting_market_outcome_types = OddsFeedBettingMarketOutcomeTypeSerializer(many=True, read_only=True)
    betting_event = BettingEventSerializer(read_only=True)
    player = PlayerSerializer(read_only=True)
    team = serializers.SlugRelatedField(slug_field='sd_team_key', read_only=True)
    bet_type = serializers.SlugRelatedField(slug_field='bet_type_name', read_only=True)
    betting_period_type = serializers.SlugRelatedField(slug_field='betting_period_type_name', read_only=True)
    betting_market_type = serializers.SlugRelatedField(slug_field='betting_market_type_id', read_only=True)

    class Meta:
        model = BettingMarket
        fields = ('id', 'betting_market_id', 'betting_event', 'betting_period_type', 'bet_type', 'player', 'team', 'betting_market_outcome_types', 'betting_market_type')


class WatchListSerializer(serializers.ModelSerializer):
    watchlist = serializers.SlugRelatedField(slug_field='id', read_only=True)

    class Meta:
        model = User
        fields = ('watchlist')


class BettingMarketSerializer(serializers.ModelSerializer):
    betting_event = BettingEventSerializer(read_only=True)
    team = serializers.SlugRelatedField(slug_field='sd_team_key', read_only=True)
    player = PlayerSerializer(read_only=True)
    bet_type = serializers.SlugRelatedField(slug_field='bet_type_name', read_only=True)
    betting_period_type = serializers.SlugRelatedField(slug_field='betting_period_type_name', read_only=True)
    betting_market_type = serializers.SlugRelatedField(slug_field='betting_market_type_id', read_only=True)

    class Meta:
        model = BettingMarket
        fields = ('id', 'betting_market_id', 'betting_event', 'betting_period_type', 'bet_type', 'team', 'player', 'betting_market_type')


class MarketOutcomeTypeSerializer(serializers.ModelSerializer):
    betting_outcome_type = serializers.SlugRelatedField(slug_field='betting_outcome_type_name', read_only=True)
    betting_market = BettingMarketSerializer(read_only=True)
    
    class Meta:
        model = BettingMarketOutcomeType
        fields = ('id', 'betting_outcome_type', 'betting_market')


class UserBetSerializer(serializers.ModelSerializer):
    betting_market_outcome_type = MarketOutcomeTypeSerializer(read_only=True)
    user = serializers.SlugRelatedField(slug_field='id', read_only=True)
    
    class Meta:
        model = UserBet
        fields = ('id', 'user', 'betting_market_outcome_type', 'value', 'wager_amount', 'payout_american', 'placed_datetime', 'is_win', 'result_update_datetime')

