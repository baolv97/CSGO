from django.core.management.base import BaseCommand
from ...TrainingElo import trainingEloPlayer, save_winrate, save_winrate_vp, crawler_over_5etop, save_winrate_5e


class Command(BaseCommand):
    help = 'Train elo for player.'

    def handle(self, *args, **options):
        print("Train elo for player ...")
        trainingEloPlayer()
        save_winrate()
        # save_winrate_vp()
        crawler_over_5etop()
        # save_winrate_5e()
        # 1. tính elo trung bình của cả đội (cộng lại / 5)

        # 2. chia elo cho các thành viên trong team
        # (nếu thắng thì cộng theo chỉ số  rating, rating càng lớn thì cộng càng nhiều)
        # (nếu thua thì trừ theo chỉ số  rating, rating càng lớn thì trừ càng ít)

        # 3. còn lại là công thức thôi

        # chỉ cần tính độ tăng elo đội A -> đội B tự trừ
        # k = 25

        print("Process is was done...elo")