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
            for j in range(0, len(match)):
                if performances[i].match_id == match[j].id:
                    performances[i].time = match[j].time
                    break
            performances[i].save()
            print(performances[i].id)
        print("Process is was done...")
