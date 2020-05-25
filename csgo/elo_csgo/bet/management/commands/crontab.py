from django.core.management.base import BaseCommand
from ...models import *
from django.core.management import call_command
from ...views import save_winrate_5e, save_winrate_vp, crawler_over_5etop
class Command(BaseCommand):
    help = 'auto crawl'
    def handle(self, *args, **options):
        call_command('crawler_1_cs_go')
        call_command('crawler_6_get_list_player')
        call_command('crawler_7_add_column_result')
        call_command('crawler_8_add_column_bet_for_performance')
        call_command('crawler_9_train_elo_for_player')
        call_command('crawler_2_bet')
        crawler_over_5etop()
        save_winrate_5e()
        save_winrate_vp()
