from django.core.management.base import BaseCommand
from ...models import *
from datetime import timedelta
from django.db.models import Q

delta = 2


class Command(BaseCommand):
    help = 'Update pet for match in table MATCH'

    def handle(self, *args, **options):
        print("Update pet for match in table MATCH starting...")

        bets = BetMatch.objects.all()
        for bet in bets:
            name_1 = bet.team_a
            name_2 = bet.team_b

            match_1 = Match.objects.filter(Q(team_a=name_1) | Q(team_b=name_1))
            if match_1.count() == 0:
                print("name_1 : {} - {}".format(bet.id, name_1))

            match_2 = Match.objects.filter(Q(team_a=name_2) | Q(team_b=name_2))
            if match_2.count() == 0:
                print("name_2 : {} - {}".format(bet.id, name_2))

        print("Process is was done...")
