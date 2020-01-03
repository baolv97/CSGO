from django.core.management.base import BaseCommand
from ...models import *
from datetime import timedelta

delta = 2


class Command(BaseCommand):
    help = 'Update pet for match in table MATCH'

    def handle(self, *args, **options):
        print("Update pet for match in table MATCH starting...")

        c_name = 0
        c_id = 0
        bets = BetMatch.objects.all()
        for bet in bets:
            time = bet.time
            time_min = time - timedelta(minutes=60 * delta)
            time_max = time + timedelta(minutes=60 * delta)

            id_team_a = bet.id_team_a
            team_a = bet.team_a
            point_team_a = bet.point_team_a
            id_team_b = bet.id_team_b
            team_b = bet.team_b
            point_team_b = bet.point_team_b

            map_name = Match.objects.filter(team_a=team_a, team_b=team_b, point_team_a=point_team_a,
                                            point_team_b=point_team_b).filter(time__range=(time_min, time_max)).first()
            if map_name:
                c_name += 1

            map_id = Match.objects.filter(id_team_a=id_team_a, id_team_b=id_team_b, point_team_a=point_team_a,
                                          point_team_b=point_team_b).filter(time__range=(time_min, time_max)).first()

            if map_id:
                c_id += 1

        print("c_name =", c_name)
        print("c_id =", c_id)
        print("sync =", c_name == c_id)
        print("Process is was done...")
