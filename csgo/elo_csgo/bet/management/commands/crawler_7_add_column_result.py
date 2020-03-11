from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Add column result'

    def get_team_win(self, match):
        return match.team_a if match.point_team_a > match.point_team_b else match.team_b

    def handle(self, *args, **options):
        print("Add column result starting...")

        performances = Performance.objects.all()

        for i in range(176000, len(performances)):
            performances[i].result = 0
            print(performances[i].id)
            if performances[i].team == self.get_team_win(performances[i].match):
                performances[i].result = 1
            performances[i].save()

        print("Process is was done...")
