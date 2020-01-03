from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Add column result'

    def get_team_win(self, match):
        return match.team_a if match.point_team_a > match.point_team_b else match.team_b

    def handle(self, *args, **options):
        print("Add column result starting...")

        performances = Performance.objects.all()

        for item in performances:
            item.result = 0
            if item.team == self.get_team_win(item.match):
                item.result = 1
            item.save()

        print("Process is was done...")
