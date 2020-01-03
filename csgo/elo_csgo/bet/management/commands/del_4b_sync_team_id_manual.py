from django.core.management.base import BaseCommand
from ...models import *
from django.db.models import Q


def get_id_from_name(team_name):
    match = Match.objects.filter(Q(team_a=team_name) | Q(team_b=team_name)).first()
    if not match:
        return 0
    return match.id_team_a if match.team_a == team_name else match.id_team_b


class Command(BaseCommand):
    help = 'Update team_id in table BET'

    def handle(self, *args, **options):
        print("Update data team_id table BET starting...")

        # dict_id = {}
        # bets = BetMatch.objects.all()
        # for bet in bets:
        #     team_a = bet.team_a
        #     id_team_a = bet.id_team_a
        #     team_b = bet.team_b
        #     id_team_b = bet.id_team_b
        #
        #     id_a = get_id_from_name(team_a)
        #     id_b = get_id_from_name(team_b)
        #
        #     if id_team_b != id_b:
        #         dict_id.update({
        #             id_team_b: bet.id
        #         })
        #
        #     if id_team_a != id_a:
        #         dict_id.update({
        #             id_team_a: bet.id
        #         })
        #
        # for k, v in dict_id.items():
        #     print("k = {} - v = {}".format(k, v))
        print("Process is was done...")
