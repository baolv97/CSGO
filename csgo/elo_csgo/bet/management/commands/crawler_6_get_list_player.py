from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Get list Player from Performance model'

    def handle(self, *args, **options):
        print("Get list Player starting...")

        performances = Performance.objects.all()

        for item in performances:
            player = Player.objects.filter(id_player=item.id_player).first()
            if player:
                if item.team not in player.team:
                    player.team = player.team
                    player.save()
            else:
                Player.objects.create(
                    team=item.team,
                    id_player=item.id_player,
                    name=item.player
                )
                print("create new -> ({}) - {} - {}".format(item.team, item.id_player, item.player))

        print("Process is was done...")
