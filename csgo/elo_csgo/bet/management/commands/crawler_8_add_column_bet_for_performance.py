from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Add column result'

    def handle(self, *args, **options):
        print("Add column result starting...")

        performances = Performance.objects.all()

        for item in performances:
            if not item.match.bet_team_a:
                continue
            if item.team == item.match.team_a:
                item.bet = item.match.bet_team_a
            else:
                item.bet = item.match.bet_team_b
            item.save()
            print(item.id)

        print("Process is was done...")
