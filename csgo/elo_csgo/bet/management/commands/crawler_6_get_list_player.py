from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Get list Player from Performance model'

    def handle(self, *args, **options):
        print("Get list Player starting...")

        performances = Performance.objects.filter(check=0)


        for i in range(len(performances)):
            print(i)
            player = Player.objects.filter(id_player=performances[i].id_player).first()
            if player:
                print(player)
            else:
                Player.objects.create(
                    team=performances[i].team,
                    id_player=performances[i].id_player,
                    name=performances[i].player
                )
                print("create new -> ({}) - {} - {}".format(performances[i].team, performances[i].id_player, performances[i].player))

        print("Process is was done...")
