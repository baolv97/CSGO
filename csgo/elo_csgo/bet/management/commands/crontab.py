from django.core.management.base import BaseCommand
from ...models import *
from django.core.management import call_command
from ...views import save_winrate_5e, save_winrate_vp, crawler_over_5etop
class Command(BaseCommand):
    help = 'auto crawl'
    def handle(self, *args, **options):
        crawler_over_5etop()
        try:
            call_command('crawler_1_cs_go')
        except Exception as e:
            print("fail crawl over htlv")

        try:
            call_command('crawler_6_get_list_player')
        except Exception as e:
            print("fail get list player")

        try:
            call_command('crawler_8_add_column_bet_for_performance')
        except Exception as e:
            print("fail get column")

        try:
            call_command('crawler_9_train_elo_for_player')
        except Exception as e:
            print("fail traing elo")

        try:
            call_command('crawler_2_bet')
        except Exception as e:
            print("fail crawl over vpgame")

        save_winrate_5e()
        save_winrate_vp()
        save_winrate_vp()
        save_winrate_5e()
