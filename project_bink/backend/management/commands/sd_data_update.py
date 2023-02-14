from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from django.db.models import Q, F, Count
from django.utils.dateparse import parse_datetime
import requests
import pytz
import zoneinfo
from datetime import datetime
from collections import defaultdict
from django.db import transaction


from backend.models import Team, Sport, League, Player, Sportsbook, BetType, BettingMarketType, BettingPeriodType, \
                    BettingEventType, BettingOutcomeType, BettingResultType, ResultedMarket, BettingEvent, BettingMarket,\
                        Bet, BetPriceUpdate, BettingMarketOutcomeType


# SportsData.io API info
KEY = 'a73c8060ac9544888d733eb96656235d'
teamEndPoint = 'https://api.sportsdata.io/v3/nfl/scores/json/AllTeams'
playerEndPoint = 'https://api.sportsdata.io/v3/nfl/scores/json/Players'
sportsbookEndPoint = 'https://api.sportsdata.io/v3/nfl/odds/json/ActiveSportsbooks'
sdMetaDataEndPoint = 'https://api.sportsdata.io/v3/nfl/odds/json/BettingMetadata'
bettingEventsEndPoint = 'https://api.sportsdata.io/v3/nfl/odds/json/BettingEvents/'
bettingMarketsByEventEndPoint = 'https://api.sportsdata.io/v3/nfl/odds/json/BettingMarkets/'

# NFL specific info
sport_name = 'american_football'
sport = Sport.objects.get(sport_name=sport_name)
league_name = 'NFL'
league = League.objects.get(league_name=league_name)
season = 2022

# Dictionaries to map sportsdata.io keys to model field names
team_model_keys = {'Key':'sd_team_key', 'TeamID':'sd_team_id', 'PlayerID':'sd_player_id', 'City':'city', 
    'Name':'name', 'Conference':'conference', 'Division':'division', 'FullName':'full_name', 'StadiumID':'stadium_id', 
    'PrimaryColor':'primary_color', 'SecondaryColor':'secondary_color', 'TertiaryColor':'tertiary_color', 
    'QuaternaryColor':'quaternary_color', 'WikipediaLogoUrl':'wiki_logo_url', 
    'WikipediaWordMarkUrl':'wiki_wordmark_url', 'GlobalTeamID':'sd_global_team_id', 'DraftKingsName':'draftkings_name', 
    'DraftKingsPlayerID':'draftkings_player_id', 'FanDuelName':'yahoo_name', 'FanDuelPlayerID':'yahoo_player_id', 
    'FantasyDraftName':'fantasydraft_name', 'FantasyDraftPlayerID':'fantasydraft_player_id', 'YahooName':'yahoo_name', 
    'YahooPlayerID':'yahoo_player_id'}

player_model_keys = {"PlayerID":"sd_player_id","Number":"number","FirstName":"first_name","LastName":"last_name","Position":"position",
        "Status":"status","Height":"height","Weight":"weight","BirthDate":"birth_date",
        "Experience":"experience","FantasyPosition":"fantasy_position","Active":"is_active",
        "PositionCategory":"position_category","Name":"full_name","Age":"age","ShortName":"short_name",
        "CurrentStatus":"current_status","FantasyAlarmPlayerID":"fantasy_alarm_id",
        "SportRadarPlayerID":"sport_radar_id","RotoworldPlayerID":"roto_world_id","RotoWirePlayerID":"roto_wire_id",
        "StatsPlayerID":"stats_id","SportsDirectPlayerID":"sports_direct_id","XmlTeamPlayerID":"xml_id",
        "FanDuelPlayerID":"fanduel_id","DraftKingsPlayerID":"draftkings_id","YahooPlayerID":"yahoo_id",
        "FanDuelName":"fanduel_name","DraftKingsName":"draftkings_name","YahooName":"yahoo_name",
        "FantasyDraftPlayerID":"fantasy_draft_id","FantasyDraftName":"fantasy_draft_name",
        "UsaTodayPlayerID":"usa_today_id"}

sportsbook_model_keys = {"SportsbookID":"sd_sportsbook_id", "Name":"sportsbook_name"}

bet_type_model_keys = {"RecordId":"bet_type_id", "Name":"bet_type_name"}

betting_market_type_model_keys = {"RecordId":"betting_market_type_id", "Name":"betting_market_type_name"}

betting_period_type_model_keys = {"RecordId":"betting_period_type_id", "Name":"betting_period_type_name"}

betting_event_type_model_keys = {"RecordId":"betting_event_type_id", "Name":"betting_event_type_name"}

betting_outcome_type_model_keys = {"RecordId":"betting_outcome_type_id", "Name":"betting_outcome_type_name"}

resulted_market_model_keys = {"BettingMarketTypeId":"betting_market_type_id", "BettingBetTypeId":"bet_type_id",
        "BettingPeriodTypeId":"betting_period_type_id"}

betting_result_type_model_keys = {"RecordId":"betting_result_type_id", "Name":"betting_result_type_name"}

betting_event_model_keys = {"BettingEventID":"betting_event_id","Name":"betting_event_name","Season":"betting_event_season","BettingEventTypeID":"betting_event_type_id",
    "BettingEventType":"betting_event_type_name","StartDate":"start_datetime","Created":"created_datetime",
    "Updated":"updated_datetime","ScoreID":"score_id","GlobalScoreID":"global_score_id","GameStatus":"game_status","Quarter":"quarter",
    "AwayTeamScore":"away_team_score","HomeTeamScore":"home_team_score","TotalScore":"total_score","GameStartTime":"game_start_datetime"}

betting_market_model_keys = {"BettingMarketID":"betting_market_id","Name":"betting_market_name",
    "Created":"created_datetime","Updated":"updated_datetime","AnyBetsAvailable":"is_bet_available"}

bet_model_keys = {"Participant":"participant","IsAvailable":"is_available","IsAlternate":"is_alternate",
    "Updated":"updated_datetime", "IsInPlay":"is_in_play", "SportsbookMarketID":"sportsbook_market_id"}

bet_price_update_model_keys = {"BettingOutcomeID":"betting_outcome_id","PayoutAmerican":"payout_american", "PayoutDecimal":"payout_decimal",
    "Value":"value", "IsAvailable":"is_available", "Created":"created_datetime", "Updated":"updated_datetime",
    "SportsbookOutcomeID":"sportsbook_outcome_id", "SportsbookUrl":"sportsbook_url", "Unlisted":"unlisted_datetime",}

check_price_update_model_keys = {"PayoutAmerican":"payout_american", "PayoutDecimal":"payout_decimal",
    "Value":"value", "IsAvailable":"is_available"}


# Helper function to bulk create objects for models
class BulkCreateManager(object):
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=100):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))


# Helper function to convert datetime fields to timezone aware objects
def convertField(field_name, value):
        if field_name[-8:]=='datetime':
            dt = parse_datetime(value)
            val = dt.replace(tzinfo=zoneinfo.ZoneInfo('America/New_York'))
        else:
            val = value
        return(val)


# Helper function to update fields on objects that already exist in database
def updateField(object, field_name, value):
    if value is not None:
        val = convertField(field_name, value)
        if getattr(object, field_name) != val:
            setattr(object, field_name, val)
            object.last_updated_utc = timezone.now()


# Establish BettingOutcome foreign key dictionaries for function below
def getForeignKeyDictionaries(betting_event_object, market_bool):
    # Get list of ids for foreign keys accessed below - goal is to reference 'id' field and avoid calling database for each fk

    player_tuple = Player.objects.all().values_list('sd_player_id','id')
    player_dict = dict((x, y) for x, y in player_tuple)

    team_tuple = Team.objects.all().values_list('sd_team_id','id')
    team_dict = dict((x, y) for x, y in team_tuple)

    sportsbook_tuple = Sportsbook.objects.all().values_list('sd_sportsbook_id','id')
    sportsbook_dict = dict((x, y) for x, y in sportsbook_tuple)

    betting_market_type_tuple = BettingMarketType.objects.all().values_list('betting_market_type_id','id')
    betting_market_type_dict = dict((x, y) for x, y in betting_market_type_tuple)
    
    bet_type_tuple = BetType.objects.all().values_list('bet_type_id','id')
    bet_type_dict = dict((x, y) for x, y in bet_type_tuple)

    betting_period_type_tuple = BettingPeriodType.objects.all().values_list('betting_period_type_id','id')
    betting_period_type_dict = dict((x, y) for x, y in betting_period_type_tuple)

    betting_outcome_type_tuple = BettingOutcomeType.objects.all().values_list('betting_outcome_type_id','id')
    betting_outcome_type_dict = dict((x, y) for x, y in betting_outcome_type_tuple)

    if market_bool == True:
        betting_market_tuple = BettingMarket.objects.filter(betting_event=betting_event_object).values_list('betting_market_id','id')
        betting_market_dict = dict((x, y) for x, y in betting_market_tuple)

        betting_market_outcome_type_tuple = BettingMarketOutcomeType.objects.filter(betting_market__in=BettingMarket.objects.filter(betting_event=betting_event_object)).values_list('market_outcome_type_combo','id')
        betting_market_outcome_type_dict = dict((x, y) for x, y in betting_market_outcome_type_tuple)
    
    else:
        betting_market_dict = None
        betting_market_outcome_type_dict = None

    return {"player_dict":player_dict,
            "team_dict":team_dict,
            "sportsbook_dict":sportsbook_dict,
            "betting_market_type_dict":betting_market_type_dict,
            "bet_type_dict":bet_type_dict,
            "betting_period_type_dict":betting_period_type_dict,
            "betting_outcome_type_dict":betting_outcome_type_dict,
            "betting_market_dict":betting_market_dict,
            "betting_market_outcome_type_dict":betting_market_outcome_type_dict}


# Helper function to get foreign keys for a betting market
def getMarketForeignKeys(market_json, betting_event_object, dictionaries):

    foreign_key_models = {"player":Player,
        "team":Team,
        "betting_market_type":BettingMarketType,
        "bet_type":BetType,
        "betting_period_type":BettingPeriodType}
    
    foreign_key_API_ids = {"player":"PlayerID",
        "team":"TeamID",
        "betting_market_type":"BettingMarketTypeID",
        "bet_type":"BettingBetTypeID",
        "betting_period_type":"BettingPeriodTypeID"}

    foreign_key_dicts = {"player":dictionaries["player_dict"],
        "team":dictionaries["team_dict"],
        "betting_market_type":dictionaries["betting_market_type_dict"],
        "bet_type":dictionaries["bet_type_dict"],
        "betting_period_type":dictionaries["betting_period_type_dict"]}

    foreign_keys = {}

    for fkey in foreign_key_models:
        if fkey == 'sportsbook':
            data = market_json['SportsBook']
        else:
            data = market_json
        if data[foreign_key_API_ids[fkey]] is None:
            if (fkey == 'team') or (fkey == 'player'):
                foreign_keys[f"{fkey}_id"] = None
            else:
                foreign_keys[f"{fkey}_id"] = foreign_key_dicts[fkey][6666666]
        else:
            try: 
                foreign_keys[f"{fkey}_id"] = foreign_key_dicts[fkey][data[foreign_key_API_ids[fkey]]]
            except:
                #print(fkey)
                foreign_keys[f"{fkey}_id"] = foreign_key_dicts[fkey][9999999]

    return foreign_keys

# Helper function to get foreign keys for a betting outcome
def getMarketOutcomeTypeForeignKeys(outcome_json, dictionaries):

    foreign_key_models = {
        "betting_market":BettingMarket,
        "betting_outcome_type":BettingOutcomeType,
        }
    
    foreign_key_API_ids = {
        "betting_market":"BettingMarketID",
        "betting_outcome_type":"BettingOutcomeTypeID",
        }

    foreign_key_dicts = {
        "betting_market":dictionaries["betting_market_dict"],
        "betting_outcome_type":dictionaries["betting_outcome_type_dict"],
        }
    
    foreign_keys = {}
    
    data = outcome_json
    for fkey in foreign_key_models:
        if data[foreign_key_API_ids[fkey]] is None:
            foreign_keys[f"{fkey}_id"] = foreign_key_dicts[fkey][6666666]
        else:
            try: 
                foreign_keys[f"{fkey}_id"] = foreign_key_dicts[fkey][data[foreign_key_API_ids[fkey]]]
            except:
                foreign_keys[f"{fkey}_id"] = foreign_key_dicts[fkey][9999999]

    return foreign_keys


# Helper function to get foreign keys for a betting outcome
def getBetForeignKeys(outcome_json, dictionaries, market_outcome_type_bool):

    foreign_key_models = {
        "player":Player,
        "team":Team,
        "sportsbook":Sportsbook}
    
    foreign_key_API_ids = {
        "player":"PlayerID",
        "team":"TeamID",
        "sportsbook":"SportsbookID"}

    foreign_key_dicts = {
        "player":dictionaries["player_dict"],
        "team":dictionaries["team_dict"],
        "sportsbook":dictionaries["sportsbook_dict"]}
    
    foreign_keys = {}
    
    for fkey in foreign_key_models:
        if fkey == 'sportsbook':
            data = outcome_json['SportsBook']
        else:
            data = outcome_json
        if data[foreign_key_API_ids[fkey]] is None:
            if (fkey == 'team') or (fkey == 'player'):
                    foreign_keys[f"{fkey}_id"] = None
            else:
                foreign_keys[f"{fkey}_id"] = foreign_key_dicts[fkey][6666666]
        else:
            try: 
                foreign_keys[f"{fkey}_id"] = foreign_key_dicts[fkey][data[foreign_key_API_ids[fkey]]]
            except:
                foreign_keys[f"{fkey}_id"] = foreign_key_dicts[fkey][9999999]
    
    if market_outcome_type_bool == True:
        if outcome_json['BettingOutcomeTypeID'] is not None:
            foreign_keys['betting_market_outcome_type_id'] = dictionaries["betting_market_outcome_type_dict"][f"{outcome_json['BettingMarketID']}-{outcome_json['BettingOutcomeTypeID']}"]
        else:
            foreign_keys['betting_market_outcome_type_id'] = dictionaries["betting_market_outcome_type_dict"][f"{outcome_json['BettingMarketID']}-0"]

    return foreign_keys


# Update teams
def fetchTeams():
    model_dict = team_model_keys
    response = requests.get(f'{teamEndPoint}?key={KEY}')
    obj = response.json()
    
    for i in obj:
        # Check if already in database
        i_count = Team.objects.filter(sd_team_id=i['TeamID']).count()
        
        # If not in database, add it and fill in relevant fields
        if i_count == 0:
            x = Team(sport=sport, league=league, last_updated_utc=timezone.now())
            for key in model_dict:
                if i[key] is not None:
                    setattr(x, model_dict[key], convertField(model_dict[key], i[key]))
            x.save()
        
        # If already in database, update any fields that differ from API response
        else:
            x = Team.objects.get(sd_global_team_id=i['GlobalTeamID'])
            for key in model_dict:
                updateField(x, model_dict[key], i[key])
            x.save()


# Update players
def fetchPlayers():
    model_dict = player_model_keys
    response = requests.get(f'{playerEndPoint}?key={KEY}')
    obj = response.json()
    
    for i in obj:
        # Check if already in database
        i_count = Player.objects.filter(sd_player_id=i['PlayerID'], league=league).count()
        
        # Get team object
        if i['Team'] is not None:
            t = Team.objects.get(sd_global_team_id=i['GlobalTeamID'])
        else:
            t = None
        
        # If not in database, add it and fill in relevant fields
        if i_count == 0:
            x = Player(current_team=t, sport=sport, league=league, last_updated_utc=timezone.now())
            for key in model_dict:
                if i[key] is not None:
                    setattr(x, model_dict[key], convertField(model_dict[key], i[key]))
            x.save()
        
        # If already in database, update any fields that differ from API response
        else:
            x = Player.objects.get(sd_player_id=i['PlayerID'])
            for key in model_dict:
                updateField(x, model_dict[key], i[key])

            updateField(x, 'current_team', t)

            x.save()


# Update sportsbooks
def fetchSportsbooks():
    model_dict = sportsbook_model_keys
    response = requests.get(f'{sportsbookEndPoint}?key={KEY}')
    obj = response.json()
    
    for i in obj:
        # Check if already in database
        i_count = Sportsbook.objects.filter(sd_sportsbook_id=i['SportsbookID']).count()
        
        # If not in database, add it and fill in relevant fields
        if i_count == 0:
            x = Sportsbook(last_updated_utc=timezone.now())
            for key in model_dict:
                if i[key] is not None:
                    setattr(x, model_dict[key], convertField(model_dict[key], i[key]))
            x.save()
        
        # If already in database, update any fields that differ from API response
        else:
            x = Sportsbook.objects.get(sd_sportsbook_id=i['SportsbookID'])
            for key in model_dict:
                updateField(x, model_dict[key], i[key])

            x.save()


# Update sportsdata.io bet metadata
def fetchMetaData():
    meta_data_categories = {"BettingBetTypes":bet_type_model_keys,
                            "BettingMarketTypes":betting_market_type_model_keys,
                            "BettingPeriodTypes":betting_period_type_model_keys,
                            "BettingEventTypes":betting_event_type_model_keys,
                            "BettingOutcomeTypes":betting_outcome_type_model_keys,
                            "ResultedMarketMetaData":resulted_market_model_keys,
                            "BettingResultTypes":betting_result_type_model_keys}
    
    meta_data_models = {"BettingBetTypes":"BetType",
                            "BettingMarketTypes":"BettingMarketType",
                            "BettingPeriodTypes":"BettingPeriodType",
                            "BettingEventTypes":"BettingEventType",
                            "BettingOutcomeTypes":"BettingOutcomeType",
                            "ResultedMarketMetaData":"ResultedMarket",
                            "BettingResultTypes":"BettingResultType"}
    
    response = requests.get(f'{sdMetaDataEndPoint}?key={KEY}')
    obj = response.json()
    for key in meta_data_categories:
        model = apps.get_model('backend', meta_data_models[key])
        model_dict = meta_data_categories[key]
        
        for i in obj[key]:
            # Check if already in database
            identifier_key = list(model_dict.keys())[0]
            identifier_value = list(model_dict.values())[0]
            filters = {}
            filters[identifier_value] = i[identifier_key]
            i_count = model.objects.filter(**filters).count()
            
            # If not in database, add it and fill in relevant fields
            if i_count == 0:
                x = model(data_provider='sportsdata', last_updated_utc=timezone.now())
                for k in model_dict:
                    if i[k] is not None:
                        setattr(x, model_dict[k], convertField(model_dict[k], i[k]))
                
                x.save()
            
            # If already in database, update any fields that differ from API response
            else:
                x = model.objects.get(**filters)
                for k in model_dict:
                    updateField(x, model_dict[k], i[k])

                updateField(x, 'data_provider', 'sportsdata')

                x.save()

# Update betting events
def fetchBettingEvents():
    model_dict = betting_event_model_keys
    
    # Call API to get all events for season identified in global NFL variables above
    response = requests.get(f'{bettingEventsEndPoint}{season}?key={KEY}')
    obj = response.json()
    
    for i in obj:
        # Check if already in database
        i_count = BettingEvent.objects.filter(betting_event_id=i['BettingEventID']).count()
        
        # Get team objects
        if i['GlobalAwayTeamID'] is not None:
            away_t = Team.objects.get(sd_global_team_id=i['GlobalAwayTeamID'])
        else:
            away_t = None
        if i['GlobalHomeTeamID'] is not None:
            home_t = Team.objects.get(sd_global_team_id=i['GlobalHomeTeamID'])
        else:
            home_t = None

        # If not in database, add it and fill in relevant fields
        if i_count == 0:
            x = BettingEvent(sport=sport, league=league, away_team=away_t, home_team=home_t, last_updated_utc=timezone.now())
            for key in model_dict:
                if i[key] is not None:
                    setattr(x, model_dict[key], convertField(model_dict[key], i[key]))
            x.save()
        
        # If already in database, update any fields that differ from API response
        else:
            x = BettingEvent.objects.get(betting_event_id=i['BettingEventID'])
            for key in model_dict:
                updateField(x, model_dict[key], i[key])
            
            # Update foreign keys if necessary
            foreign_keys = {"away_team":away_t,
                            "home_team":home_t}
            for fkey in foreign_keys:
                updateField(x, fkey, foreign_keys[fkey])
            
            x.save()


def parseBettingMarketsByEvent(betting_event_id, betting_event_object):
    # Get markets from API
    response = requests.get(f'{bettingMarketsByEventEndPoint}{betting_event_id}?key={KEY}')
    obj = response.json()

    # Pull existing markets in db for event
    existing_markets = BettingMarket.objects.filter(betting_event=betting_event_object)
    existing_market_outcome_types = BettingMarketOutcomeType.objects.filter(betting_market__in=existing_markets)
    existing_bets_for_market = Bet.objects.filter(betting_market_outcome_type__in=existing_market_outcome_types)
    existing_bets_for_market_ids = list(existing_bets_for_market.values_list('bet_identifier', flat=True))
    existing_bets_with_prices = Bet.objects.filter(betting_market_outcome_type__in=existing_market_outcome_types, id__in=BetPriceUpdate.objects.all().values_list('bet', flat=True))
    existing_bets_with_prices_ids = list(existing_bets_with_prices.values_list('bet_identifier', flat=True))

    fetchBettingMarkets(obj, betting_event_object, existing_markets)
    fetchBettingMarketOutcomeTypes(obj, betting_event_object, existing_market_outcome_types)
    fetchBets(obj, existing_bets_for_market, existing_bets_for_market_ids, betting_event_object)
    fetchBetPriceUpdates(obj, existing_bets_with_prices, existing_bets_with_prices_ids, betting_event_object)


# Update markets for an individual betting event
def fetchBettingMarkets(obj, betting_event_object, existing_markets):

    # Assign correct dictionary for model fields (dictionaries declared above)
    model_dict = betting_market_model_keys
    
    existing_markets_ids = existing_markets.values_list('betting_market_id', flat=True)

    # Initialize variable to bulk_create BettingMarketobjects
    market_bulk_mgr = BulkCreateManager(chunk_size=100)

    # Load dictionaries that will be used to assign foreign keys for each market
    fk_dicts = getForeignKeyDictionaries(betting_event_object, market_bool=False)

    ### GET MARKETS
    # Loop through markets for event
    for i in obj:
        
        #print(i['BettingMarketID'])
        
        # Get foreign keys for market
        foreign_keys = getMarketForeignKeys(i, betting_event_object, fk_dicts)
        
        # If not in database, add it and fill in relevant fields
        if i['BettingMarketID'] not in existing_markets_ids:
            x = BettingMarket(betting_event=betting_event_object,sport=sport, league=league, last_updated_utc=timezone.now())
            
            # Input foreign keys
            for f in foreign_keys:
                setattr(x, f, foreign_keys[f])

            # Input other fields
            for key in model_dict:
                if i[key] is not None:
                    setattr(x, model_dict[key], convertField(model_dict[key], i[key]))
            market_bulk_mgr.add(x)
            
        
        # If already in database, update any fields that differ from API response
        else:
            x = existing_markets.get(betting_market_id=i['BettingMarketID'])

            # Update foreign keys if necessary
            for ff in foreign_keys:
                updateField(x, ff, foreign_keys[ff])

            # Update other fields if necessary
            for key in model_dict:
                updateField(x, model_dict[key], i[key])

            x.save()

    # Add any remaining objects in bulk_create variable to db
    market_bulk_mgr.done()
    



def fetchBettingMarketOutcomeTypes(obj, betting_event_object, existing_market_outcome_types):
    # Initialize variable to bulk_create BettingMarketOutcomeType objects
    market_outcome_type_bulk_mgr = BulkCreateManager(chunk_size=100)

    # Load foreign key dictionaries for event
    fk_dictionaries = getForeignKeyDictionaries(betting_event_object, market_bool=True)

    # Pull existing market_outcome_types for these markets
    #if existing_markets is not None:
    #    existing_market_outcome_types = BettingMarketOutcomeType.objects.filter(betting_market__in=existing_markets)
    existing_market_outcome_types_ids = existing_market_outcome_types.values_list('market_outcome_type_combo', flat=True)
    existing_market_outcome_types_ids = list(existing_market_outcome_types_ids)

    for z in obj:
        outcomes = z['BettingOutcomes']
        for a in outcomes:
            if a['BettingOutcomeTypeID'] is None:
                outcome_type_id = 0
            else:
                outcome_type_id = a['BettingOutcomeTypeID']
            #if fk_dictionaries['betting_market_outcome_type_dict'].get(f"{z['BettingMarketID']}-{outcome_type_id}") is None:
            if f"{z['BettingMarketID']}-{outcome_type_id}" not in existing_market_outcome_types_ids:
                market_outcome_type_bulk_mgr.add(addMarketOutcomeType(z['BettingMarketID'], a, fk_dictionaries))
                existing_market_outcome_types_ids.append(f"{z['BettingMarketID']}-{outcome_type_id}")
    
    # Add any remaining objects in bulk_create variable to db
    market_outcome_type_bulk_mgr.done()

import line_profiler
import atexit
profile = line_profiler.LineProfiler()
atexit.register(profile.print_stats)

@profile
def fetchBets(obj, existing_bets_for_market, existing_bets_for_market_ids, betting_event_object):
    # Load foreign key dictionaries for event
    fk_dictionaries = getForeignKeyDictionaries(betting_event_object, market_bool=True)

    # Initialize variable to bulk_create BettingOutcome objects
    bet_bulk_mgr = BulkCreateManager(chunk_size=100)

    # Loop through markets
    for j in obj:
        
        # Update market's outcomes
        outcomes = j['BettingOutcomes']
        
        # Create list to track new bets added in this loop
        new_bets = []

        for o in outcomes:
            mot_foreign_keys = getMarketOutcomeTypeForeignKeys(o, fk_dictionaries)
            bet_identifier = f"{j['BettingMarketID']}-{mot_foreign_keys['betting_outcome_type_id']}-{o['SportsBook']['SportsbookID']}-{o['PlayerID']}-{o['GlobalTeamID']}-{o['Participant']}"
            if bet_identifier in existing_bets_for_market_ids:
                # Update existing bet in db
                bet_object = existing_bets_for_market.get(bet_identifier=bet_identifier)
                updateBet(bet_object, o, fk_dictionaries)
            
            elif bet_identifier not in new_bets:
                # Add new outcome to db via bulk_create variable
                bet_bulk_mgr.add(addBet(o, bet_identifier, fk_dictionaries))
                # Add bet identifier to list of existing bets
                new_bets.append(bet_identifier)
    
    # Add any remaining objects in bulk_create variable to db
    bet_bulk_mgr.done()


def fetchBetPriceUpdates(obj, existing_bets_for_market, existing_bets_for_market_ids, betting_event_object):
    ### GET PRICE UPDATES
    # Load foreign key dictionaries for event
    fk_dictionaries = getForeignKeyDictionaries(betting_event_object, market_bool=True)
    
    bet_price_bulk_mgr = BulkCreateManager(chunk_size=100)
    previous_updates = []

    # Pull price updates for existing outcomes for these markets
    if existing_bets_for_market is not None:
        existing_bet_price_updates = BetPriceUpdate.objects.filter(bet__in=existing_bets_for_market).values_list('betting_outcome_id', flat=True)
    
    # Add prices for new outcomes just added above
    bet_tuple = Bet.objects.filter(
        betting_market_outcome_type__in=BettingMarketOutcomeType.objects.filter(
            betting_market__in=BettingMarket.objects.filter(betting_event=betting_event_object)
            )
            ).values_list('bet_identifier', 'id')
    #Bet.objects.filter(betting_market__in=BettingMarket.objects.filter(betting_event=betting_event_object)).values_list('betting_outcome_id','id')
    bet_dict = dict((x, y) for x, y in bet_tuple)
    for k in obj:
        
        # Create list to track new price updates added in this loop
        new_prices = []

        outcomes = k['BettingOutcomes']
        for p in outcomes:
            foreign_keys = getMarketOutcomeTypeForeignKeys(p, fk_dictionaries)
            bet_identifier = f"{k['BettingMarketID']}-{foreign_keys['betting_outcome_type_id']}-{p['SportsBook']['SportsbookID']}-{p['PlayerID']}-{p['GlobalTeamID']}-{p['Participant']}"
            bet_id = bet_dict[bet_identifier]
            if bet_identifier not in existing_bets_for_market_ids and bet_identifier not in new_prices:
                # Add price update for new bet
                bet_price_bulk_mgr.add(addBetPrice(p, bet_id))
                new_prices.append(bet_identifier)
            
            # Add new price update for existing bet if price update with same outcome id doesn't already exist
            elif p['BettingOutcomeID'] not in existing_bet_price_updates:
                try:
                    #print(f"{bet_identifier} {bet_id}")
                    # Add new price update if prices in json differ from previous price update
                    bet_most_recent_price_update = BetPriceUpdate.objects.filter(bet_id=bet_id).latest('created_datetime')
                except:
                    # Save all price updates still in bulk create manager, then get most recent update, then create new bulk manager instance
                    bet_price_bulk_mgr.done()
                    bet_most_recent_price_update = BetPriceUpdate.objects.filter(bet_id=bet_id).latest('created_datetime')
                    bet_price_bulk_mgr = BulkCreateManager(chunk_size=100)
                if convertField('created_datetime', p['Created']) > bet_most_recent_price_update.created_datetime:
                    if checkPriceChanges(bet_most_recent_price_update, p) > 0:
                        bet_price_bulk_mgr.add(addPriceExistingBet(bet_most_recent_price_update, p, bet_id))
                        previous_updates.append(bet_most_recent_price_update.id)
    
    # Add any remaining objects in bulk_create variable to db
    bet_price_bulk_mgr.done()
    
    if len(previous_updates) > 0:
        with transaction.atomic():
            for update in previous_updates:
                BetPriceUpdate.objects.filter(id=update).update(is_most_recent_update=False)


# Add new betting market outcome type
def addMarketOutcomeType(betting_market_id, outcome_json, fk_dictionaries):
    foreign_keys = getMarketOutcomeTypeForeignKeys(outcome_json, fk_dictionaries)
    if outcome_json['BettingOutcomeTypeID'] is None:
        outcome_type_id = 0
    else:
        outcome_type_id = outcome_json['BettingOutcomeTypeID']

    mot_object = BettingMarketOutcomeType(
        market_outcome_type_combo = f"{betting_market_id}-{outcome_type_id}"
    )
    setattr(mot_object, 'betting_market_id', foreign_keys['betting_market_id'])
    setattr(mot_object, 'betting_outcome_type_id', foreign_keys['betting_outcome_type_id'])
    return mot_object


# Add new betting outcome
def addBet(outcome_json, bet_identifier, fk_dictionaries):
    model_dict = bet_model_keys

    # If not in database, add it and fill in relevant fields
    bet_object = Bet(bet_identifier = bet_identifier, sport=sport, league=league, last_updated_utc=timezone.now())
    
    # Input foreign keys
    foreign_keys = getBetForeignKeys(outcome_json, fk_dictionaries, market_outcome_type_bool=True)
    for f in foreign_keys:
        setattr(bet_object, f, foreign_keys[f])
    
    #Input other fields
    for key in model_dict:
        if outcome_json[key] is not None:
            setattr(bet_object, model_dict[key], convertField(model_dict[key], outcome_json[key]))

    return bet_object


# Update existing betting outcome if any fields have changed
def updateBet(bet_object, outcome_json, fk_dictionaries):
    model_dict = bet_model_keys
    
    # If already in database, update any fields that differ from API response
    dt = parse_datetime(outcome_json['Updated'])
    val = dt.replace(tzinfo=zoneinfo.ZoneInfo('America/New_York'))
    if bet_object.updated_datetime > val:
        for key in model_dict:
            updateField(bet_object, model_dict[key], outcome_json[key])

        # Update foreign keys if necessary
        foreign_keys = getBetForeignKeys(outcome_json, fk_dictionaries, market_outcome_type_bool=True)
        for ff in foreign_keys:
            updateField(bet_object, ff, foreign_keys[ff])

        bet_object.save()


# Add first price update for a betting outcome
def addBetPrice(outcome_json, bet_id):
    model_dict = bet_price_update_model_keys
    
    x = BetPriceUpdate(bet_id=bet_id, data_provider='sportsdata', is_first_update=True, is_most_recent_update=True,
        previous_update=None, last_updated_utc=timezone.now())
    
    for key in model_dict:
        if outcome_json[key] is not None:
            setattr(x, model_dict[key], convertField(model_dict[key], outcome_json[key]))
            if key == 'PayoutAmerican' and outcome_json['BettingOutcomeID'] == 43987003:
                id = outcome_json['BettingOutcomeID']
                val = outcome_json['PayoutAmerican']
                print(f'addBetPrice {id} {val}')

    return x
    
# Check whether payouts or value in price update differs from previous update for that outcome
def checkPriceChanges(previous_update, outcome_json):
    model_dict = check_price_update_model_keys

    change_count = 0
    for key in model_dict:
        if outcome_json[key] is not None:
            bet_identifier = previous_update.bet.bet_identifier
            #print(f"{bet_identifier}-{key}-{getattr(previous_update, model_dict[key])}-{outcome_json[key]}")
            if round(float(getattr(previous_update, model_dict[key])),1) != round(float(convertField(model_dict[key],outcome_json[key])),1):
                #print(f"{model_dict[key]}-{key}: {round(getattr(previous_update, model_dict[key]),1)} != {round(convertField(model_dict[key],outcome_json[key]),1)}")
                change_count += 1
    
    return change_count

# Add a price update for a betting outcome that already has at least one price update
def addPriceExistingBet(previous_update, outcome_json, bet_id):
    model_dict = bet_price_update_model_keys
    
    # If payouts or values are different, create new price update and edit fields for previous update where necessary
    x = BetPriceUpdate(bet_id=bet_id, is_first_update=False, is_most_recent_update=True,
    previous_update=previous_update, last_updated_utc=timezone.now())
    for key in model_dict:
        if outcome_json[key] is not None:
            setattr(x, model_dict[key], convertField(model_dict[key], outcome_json[key]))
            if key == 'PayoutAmerican' and outcome_json['BettingOutcomeID'] == 43987003:
                id = outcome_json['BettingOutcomeID']
                val = outcome_json['PayoutAmerican']
                print(f'addPriceExistingBet {id} {val}')
    return x


# Loop through events and update markets as needed
def updateMarkets():
    # Pull events that have been updated since the last time their markets were updated
    tz = pytz.timezone('EST')
    now_est = datetime.now(tz)
    
    # Get list of all outcome ids
    #global existing_outcome_ids 
    #existing_outcome_ids = BettingOutcome.objects.values_list('betting_outcome_id', flat=True)
    
    #events = BettingEvent.objects.filter(Q(last_updated_utc__gte=F('last_markets_update_utc')) | Q(last_markets_update_utc__isnull=True) | Q(start_datetime__gte=now_est))
    #events = BettingEvent.objects.all()
    #for betting_event_object in events:
    #    if betting_event_object.betting_event_type_id==1:
    betting_event_object=BettingEvent.objects.get(betting_event_id=623)
    e = betting_event_object.betting_event_id
    print(e) #.betting_event_id
    parseBettingMarketsByEvent(e, betting_event_object) #.betting_event_id
    now_utc = timezone.now()
    event = BettingEvent.objects.get(betting_event_id=e)
    event.last_updated_utc = now_utc
    event.last_markets_update_utc = now_utc
    event.save()


def adjustPlayerProps():
    # Filter on bets with players
    starting_bets = Bet.objects.filter(player__isnull=False)
    
    # Get list of market-outcome-types for the bets above that have a non-null 'value' field
    starting_market_outcome_type_ids = []
    for bet in starting_bets:
        if bet.most_recent_value() is not None:
            starting_market_outcome_type_ids.append(bet.betting_market_outcome_type_id)
    starting_market_outcome_types = BettingMarketOutcomeType.objects.filter(id__in=starting_market_outcome_type_ids)

    # Get corresponding list of markets
    starting_markets = BettingMarket.objects.filter(id__in=starting_market_outcome_types.values('betting_market_id'))
    
    # Filter on markets that have exactly 2 outcome types
    two_outcome_type_markets = starting_markets.annotate(ot_count=Count('betting_market_outcome_types')).filter(ot_count=2)

    # Adjust these fields for these markets:
        # Market type - player props
    event_object = BettingEvent.objects.get(betting_event_id=956)
    market_type_object = BettingMarketType.objects.get(betting_market_type_id=2)
    over_object = BettingOutcomeType.objects.get(betting_outcome_type_id=3)
    under_object = BettingOutcomeType.objects.get(betting_outcome_type_id=4)
    for m in two_outcome_type_markets:
        setattr(m, 'betting_market_type', market_type_object)
        m.save()
        
        # Adjust these fields for remaining market-outcome-types:
            # Outcome types - over and under
        mots = m.betting_market_outcome_types.all()
        over = mots.order_by('betting_outcome_type__id').first()
        over.betting_outcome_type = over_object
        #print(f"{over.id}-{over.betting_outcome_type.betting_outcome_type_name}-{over_object.betting_outcome_type_name}")
        over.save()

        under = mots.order_by('betting_outcome_type__id').last()
        under.betting_outcome_type = under_object
        #print(f"{under.id}-{under.betting_outcome_type.betting_outcome_type_name}-{under_object.betting_outcome_type_name}")
        under.save()
    
def checkMostRecentUpdate():
    updates = BetPriceUpdate.objects.filter(is_most_recent_update=True)
    bets = updates.values_list('bet', flat=True)
    zero_bets = Bet.objects.exclude(id__in=bets)
    if len(zero_bets) > 0:
        for bet in zero_bets:
            bet_updates = list(bet.bet_price_updates.all())
            if len(bet_updates) > 0:
                bet_updates.sort(key=lambda x: x.created_datetime, reverse=True)
                to_update = bet_updates[0]
                to_update.is_most_recent_update = True
                to_update.save()
                print('updated most recent')
    to_falsify = []
    for bet in bets:
        bet_updates2 = updates.filter(bet=bet)
        if bet_updates2.count() > 1:
            latest = bet_updates2.latest('created_datetime')
            bet_updates2 = bet_updates2.exclude(id=latest.id)
            for update in bet_updates2:
                to_falsify.append(update.id)
    
    with transaction.atomic():
        for x in to_falsify:
            BetPriceUpdate.objects.filter(id=x).update(is_most_recent_update=False)



class Command(BaseCommand):
    help = 'Calls SportsData.io APIs to update project databases'
    def handle(self, *args, **kwargs):
        #fetchTeams()
        #fetchPlayers()
        #fetchSportsbooks()
        #fetchMetaData()
        #checkMostRecentUpdate()
        #fetchBettingEvents()
        updateMarkets()
        #adjustPlayerProps()