from django.core.management.base import BaseCommand
from ...models import *
from datetime import timedelta

delta = 2


class Command(BaseCommand):
    help = 'Update pet for match in table MATCH'

    def handle(self, *args, **options):
        print("Update pet for match in table MATCH starting...")

        c = 0
        bets = BetMatch.objects.all()
        for bet in bets:
            time = bet.time
            time_min = time - timedelta(minutes=60 * delta)
            time_max = time + timedelta(minutes=60 * delta)

            # id_team_a = bet.id_team_a
            team_a = bet.team_a
            point_team_a = bet.point_team_a
            # id_team_b = bet.id_team_b
            team_b = bet.team_b
            point_team_b = bet.point_team_b

            match = Match.objects.filter(team_a=team_a, team_b=team_b, point_team_a=point_team_a,
                                         point_team_b=point_team_b, time__range=(time_min, time_max)).first()

            if match and (not match.bet_team_a) and (not match.bet_team_a):
                c += 1
                match.bet_team_a = bet.bet_team_a
                match.bet_team_b = bet.bet_team_b
                match.source_bet = bet.source
                match.save()
                print("match_id = {} update success.".format(match.id))
            # else:
            #     print(bet)

        print("{} MATCH UPDATED BET.".format(c))
        print("Process is was done...")
