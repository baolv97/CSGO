from django.core.management.base import BaseCommand
from ...models import *
from django.db.models import Q

map_name = [
    {
        "bet_name": "Team Divine",
        "match_name": "Divine",
    },
    {
        "bet_name": "Grayhound Gaming",
        "match_name": "Grayhound",
    },
    {
        "bet_name": "Team LDLC",
        "match_name": "LDLC",
    },
    {
        "bet_name": "Na`Vi",
        "match_name": "Natus Vincere",
    },
    {
        "bet_name": "TFT",
        "match_name": "The Final Tribe",
    },
    {
        "bet_name": "ex-Zone",
        "match_name": "Rugratz",
    },
    {
        "bet_name": "SuperJymy",
        "match_name": "SJ",
    },
    {
        "bet_name": "Win Scrims Not Match",
        "match_name": "Win Scrims Not Matches",
    },
    {
        "bet_name": "average25iqbutheadsh",
        "match_name": "average25iqbutheadshots",
    },
    {
        "bet_name": "Think Outside the Bo",
        "match_name": "Think Outside the Box",
    },
    # {
    #     "bet_name": "Windigo",
    #     "match_name": "ex-Windigo",
    # },
    # {
    #     "bet_name": "Luminosity",
    #     "match_name": "ex-Luminosity",
    # },
]


class Command(BaseCommand):
    help = 'Update team_name manual in table BET'

    def handle(self, *args, **options):
        print("Update team_name manual table BET starting...")

        c = 0
        for item in map_name:
            bet_name = item.get("bet_name")
            match_name = item.get("match_name")
            bets = BetMatch.objects.filter(Q(team_a=bet_name) | Q(team_b=bet_name))
            for bet in bets:
                if bet.team_a == bet_name:
                    bet.team_a = match_name
                if bet.team_b == bet_name:
                    bet.team_b = match_name
                bet.save()
                c += 1
                print("bet_id = {} update success.".format(bet.id))

        print("{} RECORD UPDATED".format(c))

        print("Process is was done...")
