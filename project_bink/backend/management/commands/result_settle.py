from django.core.management.base import BaseCommand
from django.apps import apps
from datetime import datetime
import pytz
import zoneinfo
from django.utils.dateparse import parse_datetime
import requests
from django.db import transaction
from django.db.models import F
from backend.models import BettingEvent, BettingResultType, BettingMarketOutcomeType, BetPriceUpdate, UserBet, User, BettingMarket

class Command(BaseCommand):
    help = 'Calls SportsData.io APIs to update project databases'
    def handle(self, *args, **kwargs):
        # SportsData.io API info
        KEY = 'a73c8060ac9544888d733eb96656235d'
        result_endpoint = 'https://api.sportsdata.io/v3/nfl/odds/json/BettingMarketResults/'


        dt = datetime.now()
        now = dt.replace(tzinfo=zoneinfo.ZoneInfo('America/New_York'))

        # Get dictionary of result types
        betting_result_type_tuple = BettingResultType.objects.all().values_list('betting_result_type_id','id')
        betting_result_type_dict = dict((x, y) for x, y in betting_result_type_tuple)

        
        mot_ids = UserBet.objects.filter(is_win__isnull=True).values_list('betting_market_outcome_type', flat=True)
        mots = BettingMarketOutcomeType.objects.filter(id__in=mot_ids)
        mkt_ids = mots.all().values_list('betting_market', flat=True)
        markets = BettingMarket.objects.filter(id__in=mkt_ids, betting_event__in=BettingEvent.objects.filter(start_datetime__lt=now))
        bet_price_update_ids = UserBet.objects.filter(is_win__isnull=True).values_list('bet_price_updates', flat=True)
        outcome_ids = BetPriceUpdate.objects.filter(id__in=bet_price_update_ids).values_list('betting_outcome_id', flat=True)

        # Loop through events with start dates before current date 
        #events = BettingEvent.objects.filter(start_datetime__lt=datetime.now())
        #for event in events:
        #print(event.betting_event_id)
        # Dictionaries to store items in order to bulk update
        market_list = []
        market_outcome_type_dict = {}
        outcome_type_dict = {}
        outcome_dict = {}
        outcome_is_win_dict = {}

        # Loop through markets
        #markets = event.betting_markets.filter(result_update_datetime=None)
        for market in markets:
            print(market.betting_market_id)
            # Call results API for market
            market_endpoint = f'{result_endpoint}{market.betting_market_id}'
            response = requests.get(f'{market_endpoint}?key={KEY}')
            if response is not None:
                print('response')
                obj = response.json()
                print(obj)
                
                # Add market to market list
                market_list.append(market.betting_market_id)
                
                # Loop through market outcomes
                outcomes = obj['BettingOutcomeResults']
                print(outcomes)
                for outcome in outcomes:
                    print(outcome['BettingOutcomeID'])
                    if outcome['BettingOutcomeID'] in outcome_ids:
                        # If this market outcome type not in dictionary, add it
                        if (f"{obj['BettingMarketID']}-{outcome['BettingOutcomeTypeID']}") not in market_outcome_type_dict:
                            market_outcome_type_dict[f"{obj['BettingMarketID']}-{outcome['BettingOutcomeTypeID']}"] = outcome['ActualValue']

                        # Add result type ID to outcome dictionary
                        if outcome['BettingResultTypeID'] != 0 and outcome['BettingResultTypeID'] < 6:
                            outcome_dict[outcome['BettingOutcomeID']] = betting_result_type_dict[outcome['BettingResultTypeID']]
                        else:
                            outcome_dict[outcome['BettingOutcomeID']] = betting_result_type_dict[1]

                        # ADJUST BELOW TO KEY OFF BETTING OUTCOME ID
                        # Add result type ID to outcome_is_win_dict                        
                        #if outcome['BettingResultTypeID'] == '2':
                        #    is_win = True
                        #else:
                        #    is_win = False
                        if outcome['BettingOutcomeType'] == 'Over':
                            if float(outcome['ActualValue']) > float(outcome['BetValue']):
                                is_win=True
                            else:
                                is_win=False
                        elif outcome['BettingOutcomeType'] == 'Under':
                            if float(outcome['ActualValue']) < float(outcome['BetValue']):
                                is_win=True
                            else:
                                is_win=False
                        else:
                            is_win=None
                        outcome_is_win_dict[outcome['BettingOutcomeID']] = is_win
                        
        print(outcome_is_win_dict)
        with transaction.atomic():
            for market in market_list:
                BettingMarket.objects.filter(betting_market_id=market).update(result_update_datetime=now)

        with transaction.atomic():
            for key, value in market_outcome_type_dict.items():
                BettingMarketOutcomeType.objects.filter(market_outcome_type_combo=key).update(actual_value=value)

        with transaction.atomic():
            for key, value in outcome_dict.items():
                BetPriceUpdate.objects.filter(betting_outcome_id=key).update(betting_result_id=betting_result_type_dict[value], result_update_datetime=now)
        
        with transaction.atomic():
            for key, value in outcome_is_win_dict.items():
                UserBet.objects.filter(is_win__isnull=True, bet_price_updates__in=BetPriceUpdate.objects.filter(betting_outcome_id=key)).update(is_win=value)

        # Create dictionary of users who will have payouts applied to account balances
        bets_to_payout = UserBet.objects.filter(is_win=True, result_update_datetime__isnull=True)
        print('bets_to_payout')
        print(bets_to_payout)
        payout_dict = {}
        for bet in bets_to_payout:
            if bet.payout_american < 0:
                payout = float(bet.wager_amount) + float(bet.wager_amount) / (-float(bet.payout_american) / 100)
            elif bet.payout_american > 0:
                payout = float(bet.wager_amount) * (100 + float(bet.payout_american)) / 100
            else:
                payout = 0
            if bet.user.id in payout_dict:
                payout_dict[bet.user.id] += payout
            else:
                payout_dict[bet.user.id] = payout
        print('payout_dict')
        print(payout_dict)

        # Apply payouts to user account balances
        with transaction.atomic():
            for key, value in payout_dict.items():
                User.objects.filter(id=key).update(account_balance=F('account_balance') + value)

        bet_list = UserBet.objects.filter(is_win__isnull=False, result_update_datetime__isnull=True).values_list('id', flat=True)
        with transaction.atomic():
            for bet in bet_list:
                UserBet.objects.filter(id=bet).update(result_update_datetime=now)