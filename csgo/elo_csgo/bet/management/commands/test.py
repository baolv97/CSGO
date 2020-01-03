from django.core.management.base import BaseCommand
from ...models import *
from ...TrainingElo import trainingEloPlayer


class Command(BaseCommand):
    help = 'Train elo for player.'

    def handle(self, *args, **options):
        print("Train elo for player ...")

        trainingEloPlayer()

        print("Process is was done...")
