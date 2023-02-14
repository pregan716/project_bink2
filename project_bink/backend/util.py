import requests
import json
from datetime import datetime

from backend.models import Team


# SportsData.io API info
KEY = '1f24369ac8dc4429afc9070e22a640b1'
teamEndPoint = 'https://api.sportsdata.io/v3/nfl/scores/json/AllTeams'


team_model_keys = {'Key':'sd_key', 'TeamID':'sd_team_id', 'PlayerID':'sd_player_id', 'City':'city', 
    'Name':'name', 'Conference':'conference', 'Division':'division', 'FullName':'full_name', 'StadiumID':'stadium_id', 
    'PrimaryColor':'primary_color', 'SecondaryColor':'secondary_color', 'TertiaryColor':'tertiary_color', 
    'QuaternaryColor':'quaternary_color', 'WikipediaLogoUrl':'wiki_logo_url', 
    'WikipediaWordMarkUrl':'wiki_wordmark_url', 'GlobalTeamID':'sd_global_team_id', 'DraftKingsName':'draftkings_name', 
    'DraftKingsPlayerID':'draftkings_player_id', 'FanDuelName':'yahoo_name', 'FanDuelPlayerID':'yahoo_player_id', 
    'FantasyDraftName':'fantasydraft_name', 'FantasyDraftPlayerID':'fantasydraft_player_id', 'YahooName':'yahoo_name', 
    'YahooPlayerID':'yahoo_player_id'}

def fetchTeams():
    response = requests.get(f'{teamEndPoint}?key={KEY}')
    obj = response.json()
    for team in obj:
        # Check if team is already in database
        t_count = Team.objects.get(sd_team_id=team['TeamID']).count()
        # If team is not in database, add it and fill in relevant fields
        if t_count == 0:
            t = Team(sport='american_football', league='NFL', last_updated=datetime.now())
            for key in team_model_keys:
                if team[key]:
                    setattr(t, team_model_keys[key], team[key])
            t.save()
        # If team is already in database, update any fields that differ from API response
        else:
            t = Team.objects.get(sd_team_id=team['TeamID'])
            for key in team_model_keys:
                if team[key]:
                    if getattr(t, team_model_keys[key]) != team[key]:
                        setattr(t, team_model_keys[key], team[key])
                        t.last_updated = datetime.now()
            t.save()

fetchTeams()