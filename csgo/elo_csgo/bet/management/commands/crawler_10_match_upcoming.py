from django.core.management.base import BaseCommand
from datetime import timedelta, datetime as my_datetime
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from ...constant import *
from ...models import *
from .crawler_1_cs_go import get_text_by_tag, get_info_type_ban_pick, get_id_team_from_request, get_datetime_from_string
import logging

logger = logging.getLogger(__name__)
session = HTMLSession()


def save_match_upcoming(req_detail, source):
    txt_type = get_info_type_ban_pick(req_detail)

    id_team_a = get_id_team_from_request(req_detail, ".team1-gradient")
    id_team_b = get_id_team_from_request(req_detail, ".team2-gradient")

    team_a = get_text_by_tag(req_detail, ".team1-gradient", "div", {"class": "teamName"})
    team_b = get_text_by_tag(req_detail, ".team2-gradient", "div", {"class": "teamName"})

    if team_a and team_b:
        m, created = MatchUpcoming.objects.update_or_create(
            source=source,
            type=txt_type.get("type_match"),
            team_a=str(team_a).strip(),
            id_team_a=id_team_a,
            team_b=str(team_b).strip(),
            id_team_b=id_team_b,
            defaults={
                'time': get_datetime_from_string(req_detail)
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
    except Exception as e:
        logger.error('(Match_Upcoming) - Failed to request html HLTV: {}'.format(str(e)))


def crawler_match_upcoming_vp_game():
    request = session.get(vp_game_url)

    # try - except Exception as e:

    # content = request.html.find(div_vp_game_match_upcoming, first=True)
    print(request)
    # soup = BeautifulSoup(content.html, 'html.parser')
    # matches_upcoming = soup.findAll("div", {"class": "prediction-match-list-item"})


class Command(BaseCommand):
    help = 'Crawler data Match Upcoming starting...'

    def handle(self, *args, **options):
        print("Crawler data starting...")

        crawler_match_upcoming_hl_tv()
        # crawler_match_upcoming_vp_game()

        print("Process is was done...")
