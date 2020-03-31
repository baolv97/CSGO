from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Add column result'

    def handle(self, *args, **options):
        print("Add column result starting...")

        performances = Performance.objects.all()
        match = Match.objects.all()
        # for i in range(170000, len(performances)):
        #     print(performances[i].id)
        #     if not performances[i].match.bet_team_a:
        #         continue
        #     if performances[i].team == performances[i].match.team_a:
        #         performances[i].bet = performances[i].match.bet_team_a
        #     else:
        #         performances[i].bet = performances[i].match.bet_team_b
        #     performances[i].save()
        #     print(performances[i].id)
        for i in range(150000, len(performances)):
            match = Match.objects.filter(id=performances[i].match_id).first()
            print(match.time)
            performances[i].time = match.time
            performances[i].save()
        print("Process is was done...")
