from django.core.management.base import BaseCommand
import requests
import urllib.parse as parse
from datetime import datetime, timedelta
from ...models import *
from ...constant import *


def compare_datetime(time_1, time_2):
    return (time_1.year == time_2.year) and (time_1.month == time_2.month) and (time_1.day == time_2.day)


class Command(BaseCommand):
    """
    How to run command:
    python3 manage.py crawler_bet -as 1572593330879 -cp 08d13c3ac297a90235fc9d6dda0f28f7 -t 1572593330880
    as, cp, t get from website (http://www.vpgame.com/prediction/match/csgo/parimutuel)
    """
    help = 'Start create CS:GO - BET data'

    def handle(self, *args, **options):
        print("Crawler data CS:GO - BET starting...")
        loop = True
        i = 0
        # vp_game = BetMatch.objects.all()
        while loop:
            offset = LIMIT * i
            i += 1
            if offset > 1000:
                break
            params.update({
                'offset': offset
            })
            link = 'https://m.vpgame.com/prediction/api/prediction/matches?category=&offset='+str(offset)+'&limit=20&status=close'
            print("(offset = {}) - {}".format(offset, link))
            user_agent = 'Mozilla/5.0 (Linux; U; Android 2.2) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'
            headers = {'User-Agent': user_agent}
            r = requests.get(link, headers=headers)
            print(r, "baobao123")
            if not r.ok:
                print("(offset = {}) - Request failed.".format(offset))
                break

            data = r.json().get("data")
            if not data:
                print("(offset = {}) - Data not found.".format(offset))
                continue

            # add info bet for match
            for item in data:

                if not item.get("predictions"):
                    print("(offset = {}) - Predictions not found.".format(offset))
                    continue
                print(item.get("predictions")[0]['id'])
                link = 'https://www.vpgame.com/match/'+str(item.get("predictions")[0]['id'])+'.html'
                time = datetime.fromtimestamp(item.get("start_time"))
                time = time.replace(minute=0, second=0, microsecond=0)

                # stop all if time = 1 year ago
                if time < (datetime.now() - timedelta(days=365)):
                    loop = False
                    print("TIME < 1 YEAR AGO.")
                    break

                team_a = item.get("teams").get("left").get("short_name")
                id_team_a = item.get("teams").get("left").get("steam_team_id")
                point_team_a = item.get("teams").get("left").get("score")
                team_b = item.get("teams").get("right").get("short_name")
                id_team_b = item.get("teams").get("right").get("steam_team_id")
                point_team_b = item.get("teams").get("right").get("score")

                # get info bet
                match_winner = item.get("predictions")[0]
                bet_team_a = match_winner.get("option").get("left").get("odds")
                bet_team_b = match_winner.get("option").get("right").get("odds")
                # for x in vp_game:
                #     if x.time == time and x.team_a == team_a and x.team_b == team_b:
                #         x.source = link
                #         x.save()
                #         break
                if match_winner.get("mode_name") == WINNER:
                    b, created = BetMatch.objects.get_or_create(
                        time=time,
                        team_a=team_a.strip(),
                        point_team_a=point_team_a,
                        team_b=team_b.strip(),
                        point_team_b=point_team_b,
                        bet_team_a=bet_team_a,
                        bet_team_b=bet_team_b,
                        defaults={
                            'id_team_a': id_team_a,
                            'id_team_b': id_team_b,
                            'source': link
                        },
                    )

                    if created:
                        print("OK -> ({}) {} {}:{} {} ({}-{})".format(time.strftime("%Y-%m-%d"), team_a,
                                                                      point_team_a, point_team_b, team_b,
                                                                      bet_team_a, bet_team_b))
                    else:
                        print("existed -> ({}) bet_id = {}".format(b.time.strftime("%Y-%m-%d"), b.id))

        else:
            print("Info incorrect! Please add new value for as, cp, t in command.")

        print("Process is was done...")
