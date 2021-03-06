from django.core.management.base import BaseCommand
from datetime import timedelta, datetime as my_datetime
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from ...constant import *
from ...models import *
from .crawler_1_cs_go import get_text_by_tag, get_info_type_ban_pick, get_id_team_from_request, get_datetime_from_string
from ...TrainingElo import winrateUpComming
import logging
import requests

logger = logging.getLogger(__name__)
session = HTMLSession()


def save_match_upcoming(req_detail, source):
    txt_type = get_info_type_ban_pick(req_detail)

    id_team_a = get_id_team_from_request(req_detail, ".team1-gradient")
    id_team_b = get_id_team_from_request(req_detail, ".team2-gradient")

    team_a = get_text_by_tag(req_detail, ".team1-gradient", "div", {"class": "teamName"})
    team_b = get_text_by_tag(req_detail, ".team2-gradient", "div", {"class": "teamName"})
    s = ""
    for i in range(29, 36):
        s += source[i]
    id_source = int(s)
    if team_a and team_b:
        time = get_datetime_from_string(req_detail) - timedelta(hours=1)
        print(time, "baobao123456")
        m, created = MatchUpcoming.objects.update_or_create(
            id_source1=id_source,
            defaults={
                'time': time,
                'type': txt_type.get("type_match"),
                'team_a': str(team_a).strip(),
                'id_team_a': id_team_a,
                'team_b': str(team_b).strip(),
                'id_team_b': id_team_b,
                'source': source,
            }
        )
        return m


def get_odds_pinnacle(request, match):
    """
    function save odds_pinnacle to table BetUpcoming
    :param request:
    :param match:
    :return:
    """
    try:
        content = request.html.find(".pinnacle-odds", first=True)
        soup = BeautifulSoup(content.html, 'html.parser')
        result = soup.find_all("td", {"class": "odds-cell"})

        if len(result) == 3:
            BetUpcoming.objects.update_or_create(
                match=match,
                banker=pinnacle,
                defaults={
                    'bet_team_a': result[0].text,
                    'bet_team_b': result[2].text
                }
            )
    except Exception as e:
        logger.error('({})Failed to get_odds_pinnacle: {}'.format(".pinnacle-odds", str(e)))


def compare_time(time):
    return time < my_datetime.now().replace(hour=23, minute=59, second=59) + timedelta(days=day)


def save_info_player(request, match):
    """
    save info player of match upcoming in hltv
    :param request:
    :param match:
    :return:
    """
    try:
        content = request.html.find(".lineups", first=True)
        soup = BeautifulSoup(content.html, 'html.parser')
        result = soup.find_all("div", {"class": "lineup"})
        for team in result:
            team_name = team.find("img", {"class": "logo"}).get('title')
            players = team.find_all("div", {"class": "flagAlign"})
            for player in players:
                MatchUpcomingPlayer.objects.update_or_create(
                    match_upcoming=match,
                    team=team_name,
                    id_player=player.get('data-player-id'),
                    name=player.find("div", {"class": "text-ellipsis"}).text
                )

    except Exception as e:
        logger.error('Failed in function save_info_player: {}'.format(str(e)))


def crawler_match_upcoming_hl_tv():
    request = session.get(url_upcoming)
    try:
        content = request.html.find(div_match_upcoming, first=True)
        soup = BeautifulSoup(content.html, 'html.parser')
        matches_upcoming = soup.findAll("a", {"class": "a-reset"})

        for match in matches_upcoming:
            href = match['href']
            source = base_url + href

            print(source)
            req_detail = session.get(source)

            # get matches in 2 next day
            time = get_datetime_from_string(req_detail)
            if not compare_time(time):
                break

            match_upcoming = save_match_upcoming(req_detail, source)
            get_odds_pinnacle(req_detail, match_upcoming)
            save_info_player(req_detail, match_upcoming)

    except Exception as e:
        logger.error('(Match_Upcoming) - Failed to request html HLTV: {}'.format(str(e)))


def crawlLiveMatches():
    request = session.get("https://www.hltv.org/matches")
    result = []
    try:
        content = request.html.find('.live-matches', first=True)
        soup = BeautifulSoup(content.html, 'html.parser')
        matches_upcoming = soup.findAll("div", {"class": "live-match"})
        # print(matches_upcoming)

        for match in matches_upcoming:
            source = match.findAll("a")
            for item in source:
                s = item['href']
                s1 = ""
                for i in range(9, 16):
                    s1 += s[i]
                print(s1, "baobao")
                result.append(int(s1))
                break
            scores = match.findAll("span", {"class": "team-name"})
            for item in scores:
                print(item.string, "team")
            header = match.findAll("tr", {"class": "header"})
            for x in header:
                map = x.findAll("td", {"class": "map"})
                for item in map:
                    print(item.string)

    except Exception as e:
        logger.error('(Match_Upcoming) - Failed to request html HLTV: {}'.format(str(e)))
    return result


def crawler_match_upcoming_vp_game():
    # TODO: chưa crawl tự động được, vì trang VPGame chặn crawl, phải cần có key cho mỗi lần crawl
    request = session.get(vp_game_url)
    print(request)


# vì trang 5etop lưu tên đội khác với hltv, nên map name bằng tay
map_name = {
    "mouz": "mousesports",
    "Na'Vi": "Natus Vincere",
}


def crawler_match_upcoming_5etop():
    """
    function crawl data match upcoming 5etop
    :return:
    """
    r = requests.get(five_etop_url)
    if r.ok:
        data = r.json().get("datas").get("list")
        for item in data:
            try:
                match = item.get("offerMatch")
                time = int(match.get("time"))
                time = my_datetime.fromtimestamp(time / 1000.0)

                team_a = match.get("vs1").get("name")
                team_a = map_name.get(team_a) if map_name.get(team_a) else team_a

                team_b = match.get("vs2").get("name")
                team_b = map_name.get(team_b) if map_name.get(team_b) else team_b

                odds_team_a = match.get("vs1").get("odds")
                odds_team_b = match.get("vs2").get("odds")

                m = MatchUpcoming.objects.filter(time__year=time.year,
                                                 time__month=time.month,
                                                 time__day=time.day,
                                                 time__hour=time.hour,
                                                 team_a=team_a,
                                                 team_b=team_b
                                                 ).first()

                if m:
                    BetUpcoming.objects.update_or_create(
                        match=m,
                        banker=five_etop,
                        defaults={
                            'bet_team_a': odds_team_a,
                            'bet_team_b': odds_team_b
                        }
                    )
            except Exception as e:
                logger.error('Failed in function crawler_match_upcoming_5etop: {}'.format(str(e)))


class Command(BaseCommand):
    help = 'Crawler data Match Upcoming starting...'

    def handle(self, *args, **options):
        print("Crawler data starting...")
        MatchUpcomingPlayer.objects.all().delete()
        # MatchUpcoming.objects.all().delete()
        crawler_match_upcoming_hl_tv()
        # crawler_match_upcoming_vp_game()
        # crawler_match_upcoming_5etop()
        winrateUpComming()
        print("Process is was done...")
