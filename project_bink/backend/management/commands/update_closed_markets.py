from django.core.management.base import BaseCommand
from django.apps import apps
import requests
from backend.models import BettingEvent, BettingMarket, BettingMarketOutcomeType, BettingOutcomeType, Bet, BetPriceUpdate, Team, Player, BettingOutcomeType, BettingMarketType, BetType, BettingPeriodType
from django.db import transaction


# TODO: Update these fields
# Markets: BettingMarketTypeID, BetTypeID, BettingPeriodTypeID, PlayerID, TeamID
# Market outcome types: OutcomeTypeID
# Outcomes: OutcomeTypeID, value


class Command(BaseCommand):
    help = 'Calls SportsData.io APIs to update project databases'
    def handle(self, *args, **kwargs):
        # API parameters
        KEY = 'a73c8060ac9544888d733eb96656235d'
        result_endpoint = 'https://api.sportsdata.io/v3/nfl/odds/json/BettingMarketResults/'

        # Lookups

        betting_market_type_tuple = BettingMarketType.objects.all().values_list('betting_market_type_id','id')
        betting_market_type_lookup = dict((x, y) for x, y in betting_market_type_tuple)

        bet_type_tuple = BetType.objects.all().values_list('bet_type_id','id')
        bet_type_lookup = dict((x, y) for x, y in bet_type_tuple)

        betting_period_type_tuple = BettingPeriodType.objects.all().values_list('betting_period_type_id','id')
        betting_period_type_lookup = dict((x, y) for x, y in betting_period_type_tuple)

        player_tuple = Player.objects.all().values_list('sd_player_id','id')
        player_lookup = dict((x, y) for x, y in player_tuple)

        team_tuple = Team.objects.all().values_list('sd_team_id','id')
        team_lookup = dict((x, y) for x, y in team_tuple)

        # Initialize dictionaries to compile fields that must be updated
        market_type_dict = {} # Key = marketid
        bet_type_dict = {} # Key = marketid
        betting_period_type_dict = {} # Key = marketid
        player_dict = {} # Key = marketid
        team_dict = {} # Key = marketid
        bet_player_dict = {} # Key = bet
        bet_team_dict = {} # Key = bet
        mot_dict = {} # Key = Bet
        value_dict = {} # Key = bet price update
        
        # Specify event to update markets for
        event_id = 623
        event_obj = BettingEvent.objects.get(betting_event_id=event_id)

        # Get markets for event
        markets = event_obj.betting_markets.all()

        # Get Market outcome types
        mots = BettingMarketOutcomeType.objects.filter(betting_market__in=markets)

        # Get bet price updates
        bets = Bet.objects.filter(betting_market_outcome_type__in=mots)
        bpus = BetPriceUpdate.objects.filter(bet__in=bets)

        # Get outcome IDs
        outcome_ids = bpus.values_list('betting_outcome_id', flat=True)

        # Loop through markets and update relevant fields in relevant objects
        for market in markets:
            print(market.betting_market_id)

            # Call API
            market_endpoint = f'{result_endpoint}{market.betting_market_id}'
            response = requests.get(f'{market_endpoint}?key={KEY}')
            if response is not None:
                obj = response.json()
                market_type_dict[market.id] = betting_market_type_lookup[int(obj['BettingMarketTypeID'])]
                bet_type_dict[market.id] = bet_type_lookup[int(obj['BettingBetTypeID'])]
                betting_period_type_dict[market.id] = betting_period_type_lookup[int(obj['BettingPeriodTypeID'])]
                if obj['PlayerID'] is not None:
                    player_dict[market.id] = player_lookup[int(obj['PlayerID'])]
                if obj['TeamID'] is not None:
                    team_dict[market.id] = team_lookup[int(obj['TeamID'])]

                outcomes = obj['BettingOutcomeResults']
                for outcome in outcomes:
                    if int(outcome['BettingOutcomeID']) in outcome_ids:
                        bpu = bpus.get(betting_outcome_id=int(outcome['BettingOutcomeID']))
                        if outcome['BetValue'] is not None:
                            value_dict[bpu.id] = float(outcome['BetValue'])
                        
                        bet = bpu.bet

                        if obj['PlayerID'] is not None and bet.id not in bet_player_dict:
                            bet_player_dict[bet.id] = player_lookup[int(obj['PlayerID'])]
                        if obj['TeamID'] is not None and bet.id not in bet_team_dict:
                            bet_team_dict[bet.id] = team_lookup[int(obj['TeamID'])]
                        
                        # Check if betting market outcome type exists
                        if bet.id not in mot_dict:
                            try:
                                mot = mots.get(betting_market=market, betting_outcome_type__betting_outcome_type_id=outcome['BettingOutcomeTypeID'])
                                mot_dict[bet.id] = mot.id
                            except:
                                bot = BettingOutcomeType.objects.get(betting_outcome_type_id=outcome['BettingOutcomeTypeID'])
                                new_mot = BettingMarketOutcomeType(
                                    betting_market=market,
                                    betting_outcome_type=bot,
                                    market_outcome_type_combo=f'{market.betting_market_id}-{bot.betting_outcome_type_id}'
                                )
                                new_mot.save()
                                mot_dict[bet.id] = new_mot.id

        # Update objects
        # Update market type
        with transaction.atomic():
            for key, value in market_type_dict.items():
                BettingMarket.objects.filter(id=key).update(betting_market_type_id=value)

        # Update bet type
        with transaction.atomic():
            for key, value in bet_type_dict.items():
                BettingMarket.objects.filter(id=key).update(bet_type_id=value)

        # Update betting period type
        with transaction.atomic():
            for key, value in betting_period_type_dict.items():
                BettingMarket.objects.filter(id=key).update(betting_period_type_id=value)
        

        # Update player for markets
        with transaction.atomic():
            for key, value in player_dict.items():
                BettingMarket.objects.filter(id=key).update(player_id=value)

        # Update team for markets
        with transaction.atomic():
            for key, value in team_dict.items():
                BettingMarket.objects.filter(id=key).update(team_id=value)

        # Update player for bets
        with transaction.atomic():
            for key, value in bet_player_dict.items():
                Bet.objects.filter(id=key).update(player_id=value)

        # Update team for bets
        with transaction.atomic():
            for key, value in bet_team_dict.items():
                Bet.objects.filter(id=key).update(team_id=value)

        # Update market outcome type
        with transaction.atomic():
            for key, value in mot_dict.items():
                Bet.objects.filter(id=key).update(betting_market_outcome_type_id=value)

        # Update market outcome type
        with transaction.atomic():
            for key, value in value_dict.items():
                BetPriceUpdate.objects.filter(id=key).update(value=value)