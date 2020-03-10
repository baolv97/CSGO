from django.core.management.base import BaseCommand
from ...TrainingElo import trainingEloPlayer
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Train elo for player.'

    def handle(self, *args, **options):
        print("Train elo for player ...")
        call_command('crawler_1_cs_go')
        call_command('crawler_6_get_list_player')
        call_command('crawler_7_add_column_result')
        call_command('crawler_8_add_column_bet_for_performance')
        trainingEloPlayer()
        # 1. tính elo trung bình của cả đội (cộng lại / 5)

        # 2. chia elo cho các thành viên trong team
        # (nếu thắng thì cộng theo chỉ số  rating, rating càng lớn thì cộng càng nhiều)
        # (nếu thua thì trừ theo chỉ số  rating, rating càng lớn thì trừ càng ít)

        # 3. còn lại là công thức thôi

        # chỉ cần tính độ tăng elo đội A -> đội B tự trừ
        # k = 25

        print("Process is was done...elo")