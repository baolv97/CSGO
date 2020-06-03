from django.core.management.base import BaseCommand
from ...models import *


class Command(BaseCommand):
    help = 'Add column result'

    def get_team_win(self, match):
        return match.team_a if match.point_team_a > match.point_team_b else match.team_b

    def handle(self, *args, **options):
        print("Add column result starting...")

        re = Result.objects.filter(check=0)
        for i in range(len(re)):
            print(re[i].id)
            break
        index = 0
        count_h = 0
        while index < len(re):
            map = re[index].map
            match_id = re[index].match_id
            point_a = re[index].point + re[index+2].point
            point_b = re[index+1].point + re[index+3].point
            team_a = re[index].team
            team_b = re[index+1].team
            ans_a = 0
            ans_b = 0
            if point_a - point_b > 0:
                ans_a = 1
                ans_b = 0
            if point_b - point_a > 0:
                ans_a = 0
                ans_b = 1
            if point_a - point_b == 0:
                count_h += 1
            for i in range(0, 4):
                re[index+i].check = 1
                re[index+i].save()
            per = Performance.objects.filter(match_id=match_id, map=map, team=team_a)
            for item in per:
                print(item.player)
                item.result = ans_a
                item.save()
            per = Performance.objects.filter(match_id=match_id, map=map, team=team_b)
            for item in per:
                print(item.player)
                item.result = ans_b
                item.save()
            index = index + 4
            print(index)
        print("Game Hoa:", count_h)

        print("Process is was done...")
