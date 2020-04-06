from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Add column result'

    def handle(self, *args, **options):
        print("Add column result starting...")

        performances = Performance.objects.all()
        for i in range(150000, len(performances)):
            if performances[i].time is not None:
                continue
            else:
                match = Match.objects.filter(id=performances[i].match_id).first()
                print(match.time)
                performances[i].time = match.time
                performances[i].save()
        print("Process is was done...")
