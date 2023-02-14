from django.contrib import admin
from .models import User, Sport, League, Team, Player, Sportsbook, BetType, BettingMarketType, BettingPeriodType, \
                    BettingEventType, BettingOutcomeType, BettingResultType, ResultedMarket, BettingEvent, BettingMarket,\
                        Bet, BetPriceUpdate, BettingMarketOutcomeType, UserBet

class BettingMarketAdmin(admin.ModelAdmin):
    list_display = ('betting_market_id', 'betting_event', 'betting_period_type', 'bet_type', 'player')

# Register your models here.
admin.site.register(BettingMarket, BettingMarketAdmin)
admin.site.register(User)
admin.site.register(Sport)
admin.site.register(League)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Sportsbook)
admin.site.register(BetType)
admin.site.register(BettingMarketType)
admin.site.register(BettingPeriodType)
admin.site.register(BettingEventType)
admin.site.register(BettingOutcomeType)
admin.site.register(BettingResultType)
admin.site.register(ResultedMarket)
admin.site.register(BettingEvent)
#admin.site.register(BettingMarket)
admin.site.register(BettingMarketOutcomeType)
admin.site.register(Bet)
admin.site.register(BetPriceUpdate)
admin.site.register(UserBet)