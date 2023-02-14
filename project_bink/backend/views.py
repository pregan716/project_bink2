import json
from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from rest_framework import viewsets
from .serializers import OddsFeedBettingMarketSerializer, WatchListSerializer, UserBetSerializer, MarketOutcomeTypeSerializer
from .models import BettingEvent, BettingMarket, Bet, BetPriceUpdate, BettingMarketOutcomeType, User, UserBet
from django.utils import timezone

# Create your views here.
def index():
    pass

# Create your views here.

class OddsFeedBettingMarketView(viewsets.ModelViewSet):
    serializer_class = OddsFeedBettingMarketSerializer
    queryset = BettingMarket.objects.filter(
        betting_market_type__betting_market_type_id__in=[2,3],
        betting_event__betting_event_id__in=[624],
        betting_period_type__betting_period_type_id=2,
        ) #, is_bet_available=True; .exclude(player__isnull=True)
    

class WatchlistView(viewsets.ModelViewSet):
    serializer_class = OddsFeedBettingMarketSerializer
    def get_queryset(self):
        return BettingMarket.objects.filter(
            id__in=self.request.user.watchlist.all().values_list('betting_market__id', flat=True)
        )
    #def get_queryset(self):
    #    return self.request.user.watchlist.all()
    

class UserBetView(viewsets.ModelViewSet):
    serializer_class = UserBetSerializer
    def get_queryset(self):
        return self.request.user.bets_placed.all()
    

# Fav or unfav bets
@login_required
def edit_watchlist(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mot_id = data.get('mot_id')
        mot = BettingMarketOutcomeType.objects.get(id=mot_id)
        user = request.user
        if user.watchlist.filter(id=mot_id).exists():
            user.watchlist.remove(mot)
            return JsonResponse({'action': 'removed'})
        else:
            user.watchlist.add(mot)
            return JsonResponse({'action': 'added'})
        


def get_csrf(request):
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response['X-CSRFToken'] = get_token(request)
    return response


def register_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        confirmation = data.get("confirmation")

        # Ensure no fields are null
        if username is None or password is None or confirmation is None:
            return JsonResponse({'detail': 'Required input missing. Please complete all fields.'}, status=400)
        
        # Ensure password matches confirmation
        if password != confirmation:
            return JsonResponse({'detail': 'Passwords do not match. Please re-enter.'}, status=400)

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
        except IntegrityError:
            return JsonResponse({'detail': 'Username already taken. Please choose another username.'}, status=400)
        
        login(request, user)
        return JsonResponse({'detail': 'Successfully registered.'})


def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if username is None or password is None:
            return JsonResponse({'detail': 'Please provide username and password.'}, status=400)

        user = authenticate(username=username, password=password)

        if user is None:
            print("user none")
            return JsonResponse({'detail': 'Invalid credentials.'}, status=400)

        login(request, user)
        return JsonResponse({'detail': 'Successfully logged in.'})


def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'You\'re not logged in.'}, status=400)

    logout(request)
    return JsonResponse({'detail': 'Successfully logged out.'})


@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'isAuthenticated': True})


def whoami_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})

    return JsonResponse({'username': request.user.username, 'account_balance': request.user.account_balance})


@login_required
def get_watchlist(request):
    user = request.user
    if user is None:
        return JsonResponse({'detail': 'Invalid credentials.'}, status=400)
    watchlist = list(user.watchlist.all().values_list('id', flat=True))
    return JsonResponse({'watchlist': watchlist})


@login_required
def place_bet(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if data.get('value') is not None:
            value = float(data.get('value'))
        else:
            value = None
        payout_american = int(data.get('payout_american'))
        wager_amount = float(data.get('wager_amount'))
        market_outcome_type_id = int(data.get('market_outcome_type_id'))
        market_outcome_type = BettingMarketOutcomeType.objects.get(id=market_outcome_type_id)
        print(market_outcome_type)
        outcome_ids = data.get('outcome_ids')
        print(outcome_ids)
        bet_price_updates = BetPriceUpdate.objects.filter(betting_outcome_id__in=outcome_ids)
        print(bet_price_updates)
        user = request.user
        current_balance = float(user.account_balance)
        if (wager_amount <= user.account_balance) & (wager_amount > 0):
            print('pre-try')
            try:
                user_bet = UserBet(
                        user=user, 
                        betting_market_outcome_type=market_outcome_type,
                        value=value,
                        payout_american=payout_american,
                        wager_amount=wager_amount,
                        placed_datetime=timezone.now()
                        )
                print('post-create')
                if wager_amount == user.account_balance:
                    user.account_balance = 100.00
                else:
                    user.account_balance = current_balance - wager_amount
                print('pre-save')
                user_bet.save()
                print('post-save')
                user_bet.bet_price_updates.add(*bet_price_updates)
                print('post-add')
                user.save()
            except:
                return JsonResponse({'detail': 'Bet could not be placed.'}, status=400)
            return JsonResponse({'detail': 'Bet succesfully placed.', 'account_balance': user.account_balance})
        else:
            return JsonResponse({'detail': 'Insufficient funds.'}, status=400)
        
@login_required
def get_bets(request):
    if request.method == 'GET':
        user = request.user
        if user is None:
            return JsonResponse({'detail': 'Invalid credentials.'}, status=400)
        bets = user.bets_placed.all()
        