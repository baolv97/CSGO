from django.core.management.base import BaseCommand
from ...models import *
from django.core.management import call_command
from ...TrainingElo import upcomming_vp, upcomming_5etop, map_up_5e, map_up_vp
class Command(BaseCommand):
    help = 'auto crawl'
    def handle(self, *args, **options):
        call_command('crawler_10_match_upcoming')
        link = "https://m.vpgame.com/prediction/api/prediction/matches?category=csgo&offset=0&limit=20&status=normal&order=asc"
        upcomming_vp(link)
        upcomming_5etop()
        map_up_5e()
        map_up_vp()


