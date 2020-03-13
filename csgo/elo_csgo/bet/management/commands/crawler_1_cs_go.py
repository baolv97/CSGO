from django.core.management.base import BaseCommand
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from ...models import *
from ...constant import *
import datetime
import dateutil.parser
import logging

logger = logging.getLogger(__name__)
session = HTMLSession()


def get_text_by_tag(request, tag_parent, tag, tag_property):
    """
    get text by tag from request
    :param request:
    :param tag_parent:
    :param tag:
    :param tag_property:
    :return: text
    """
    try:
        content = request.html.find(tag_parent, first=True)
        soup = BeautifulSoup(content.html, 'html.parser')
        result = soup.find(tag, tag_property)
        return result.text if result else None
    except Exception as e:
        logger.error('({})Failed to get_text_by_tag: {}'.format(tag_parent, str(e)))


def get_id_team_from_request(request, tag_parent):
    """
    function get id_team_a, b from request
    :param request:
    :param tag_parent:
    :return:
    """
    try:
        content = request.html.find(tag_parent, first=True)
        soup = BeautifulSoup(content.html, 'html.parser')
        src = soup.find('img')['src']
        return int(src[src.rfind("/") + 1:])
    except Exception as e:
        logger.error('({})Failed to get_id_team_from_request: {}'.format(tag_parent, str(e)))


def get_datetime_from_string(request):
    date = get_text_by_tag(request, ".timeAndEvent", "div", {"class": "date"})
    time = get_text_by_tag(request, ".timeAndEvent", "div", {"class": "time"})

    try:
        time_match = dateutil.parser.parse("{} {}".format(date, time), dayfirst=True) + datetime.timedelta(
            minutes=60 * 6)
        time_match = time_match.replace(second=0, microsecond=0)
        return time_match
    except Exception:
        return None


def get_type_math_from_string(txt_type):
    types = [1, 2, 3, 5, 7]
    bo = "Best of {}"
    for i in types:
        if bo.format(i) in txt_type:
            return bo.format(i)
    return None


def get_info_type_ban_pick(request):
    try:
        ban_pick = []
        type_match = "Best of 1"
        maps = request.html.find(".col-7-small", first=True)
        soup_maps = BeautifulSoup(maps.html, 'html.parser')
        results = soup_maps.find_all("div", {"class": "veto-box"})

        # get type_match
        if results:
            txt_type = results[0].find('div', {"class": "preformatted-text"}).text
            type_match = get_type_math_from_string(txt_type)

        # get list ban_pick
        if len(results) > 1:
            list_bp = results[1].find_all('div', {"class": ""})
            count = 0
            for item in list_bp:
                count += 1
                if REMOVED in item.text[3:]:
                    team_map = item.text[3:].split(" {} ".format(REMOVED))
                    ban_pick.append({
                        "order": count,
                        "team": team_map[0],
                        "ban": team_map[1],
                        "pick": None,
                    })
                if PICKED in item.text[3:]:
                    team_map = item.text[3:].split(" {} ".format(PICKED))
                    ban_pick.append({
                        "order": count,
                        "team": team_map[0],
                        "ban": None,
                        "pick": team_map[1],
                    })
        return {
            "type_match": type_match,
            "ban_pick": ban_pick
        }
    except Exception as e:
        logger.error('Failed to get_info_type_ban_pick: {}'.format(str(e)))


def save_match(req_detail, source):
    point_team_a_w = get_text_by_tag(req_detail, ".team1-gradient", "div", {"class": "won"})
    point_team_a_l = get_text_by_tag(req_detail, ".team1-gradient", "div", {"class": "lost"})
    point_team_b_l = get_text_by_tag(req_detail, ".team2-gradient", "div", {"class": "lost"})
    point_team_b_w = get_text_by_tag(req_detail, ".team2-gradient", "div", {"class": "won"})
    point_team_a = point_team_a_l if point_team_a_l else point_team_a_w
    point_team_b = point_team_b_l if point_team_b_l else point_team_b_w

    txt_type = get_info_type_ban_pick(req_detail)

    id_team_a = get_id_team_from_request(req_detail, ".team1-gradient")
    id_team_b = get_id_team_from_request(req_detail, ".team2-gradient")

    return Match.objects.create(
        source=source,
        time=get_datetime_from_string(req_detail),
        type=txt_type.get("type_match"),
        team_a=str(get_text_by_tag(req_detail, ".team1-gradient", "div", {"class": "teamName"})).strip(),
        id_team_a=id_team_a,
        point_team_a=point_team_a if point_team_a else get_text_by_tag(req_detail, ".team1-gradient", "div",
                                                                       {"class": "tie"}),
        team_b=str(get_text_by_tag(req_detail, ".team2-gradient", "div", {"class": "teamName"})).strip(),
        id_team_b=id_team_b,
        point_team_b=point_team_b if point_team_b else get_text_by_tag(req_detail, ".team2-gradient", "div",
                                                                       {"class": "tie"}),
    )


def save_ban_pick(match, request):
    veto_box = get_info_type_ban_pick(request)
    ban_pick = veto_box.get("ban_pick")
    for item in ban_pick:
        try:
            BanPick.objects.create(
                match=match,
                order=item.get("order"),
                team=item.get("team"),
                ban=item.get("ban"),
                pick=item.get("pick")
            )
        except Exception as e:
            logger.error('(match_id={})Failed to save BanPick: {}'.format(match.id, str(e)))
            continue


def get_result_from_string(request, map, txt_result):
    results = []
    l = txt_result.find('(')
    r = txt_result.find(')')
    result = txt_result[l + 1:r].split('; ')
    team_a = get_text_by_tag(request, ".team1-gradient", "div", {"class": "teamName"})
    team_b = get_text_by_tag(request, ".team2-gradient", "div", {"class": "teamName"})

    if len(result) == 2:
        for i in range(2):
            h = result[i].split(':')
            results.append({
                "map": map,
                "half": i + 1,
                "team": team_a,
                "point": h[0],
            })
            results.append({
                "map": map,
                "half": i + 1,
                "team": team_b,
                "point": h[1],
            })

    return results


def get_info_results(match, request):
    try:
        content = request.html.find(".flexbox-column", first=True)
        soup = BeautifulSoup(content.html, 'html.parser')
        results = soup.find_all("div", {"class": "mapholder"})

        for item in results:
            map_name = item.find("div", {"class": "mapname"})
            result = item.find("div", {"class": "results"})

            if result:
                results = get_result_from_string(request, map_name.text, result.text)
                save_result(match, results)
    except Exception as e:
        logger.error('(match_id={})Failed to request html Results: {}'.format(match.id, str(e)))


def save_result(match, objects):
    for obj in objects:
        try:
            Result.objects.create(
                match=match,
                map=obj.get("map"),
                half=obj.get("half"),
                team=obj.get("team"),
                point=obj.get("point")
            )
        except Exception as e:
            logger.error('(match_id={})Failed to save Result: {}'.format(match.id, str(e)))
            continue


def get_id_player_from_href(href):
    id_player = href[8:]
    return id_player[0:id_player.find('/')]


def save_info_table_performance(match, map_name, team, table):
    tr = table.find_all("tr", {"class": ""})
    for item in tr:
        nick_player = item.find("span", {"class": "player-nick"}).text
        k_d = item.find("td", {"class": "kd"}).text.split('-')
        kill = k_d[0]
        death = k_d[1]
        adr = item.find("td", {"class": "adr"}).text
        kast = item.find("td", {"class": "kast"}).text[:-1]
        rating = item.find("td", {"class": "rating"}).text

        href = item.find('a')['href']
        id_player = get_id_player_from_href(href)

        try:
            Performance.objects.create(
                match=match,
                map=map_name,
                team=team,
                player=nick_player,
                id_player=id_player,
                kill=kill,
                death=death,
                adr=adr,
                kast=kast,
                rating=rating
            )
        except Exception as e:
            logger.error('(match_id={})Failed to save Performance: {}'.format(match.id, str(e)))
            continue


def save_performance(match, request):
    try:
        content = request.html.find(".matchstats", first=True)
        soup = BeautifulSoup(content.html, 'html.parser')

        # get list map_name
        map_names = soup.find_all("div", {"class": "dynamic-map-name-full"})
        # get list performance
        performances = soup.find_all("div", {"class": "stats-content"})

        if len(map_names) == len(performances):
            team_a = get_text_by_tag(request, ".team1-gradient", "div", {"class": "teamName"})
            team_b = get_text_by_tag(request, ".team2-gradient", "div", {"class": "teamName"})

            for i in range(1, len(map_names)):
                map_name = map_names[i].text
                tables = performances[i].find_all("table", {"class": "table totalstats"})

                if len(tables) == 2:
                    save_info_table_performance(match, map_name, team_a, tables[0])
                    save_info_table_performance(match, map_name, team_b, tables[1])

        else:
            logger.error('else - performance: (match_id={})Failed to request html Performance'.format(match.id))
    except Exception as e:
        logger.error('(match_id={})Failed to request html Performance: {}'.format(match.id, str(e)))


class Command(BaseCommand):
    help = 'Start create CS:GO data'

    def handle(self, *args, **options):
        print("Crawler data CS:GO starting...")

        for i in range(0, (max_offset // 100)):
            # for i in range(0, 1):
            offset = i * 100
            print("offset =", offset)
            request = session.get(url.format(offset=offset))

            try:
                content = request.html.find(div_results, first=True)
                soup = BeautifulSoup(content.html, 'html.parser')
                list_match = soup.findAll("div", {"class": "result-con"})

                for match in list_match:
                    href = match.find('a')['href']
                    source = base_url + href

                    # skip = Match.objects.filter(source=source).first() if source else True
                    # if skip:
                    #     print("existed -> {}".format(source))
                    #     continue

                    print(source)
                    req_detail = session.get(source)
                    match = save_match(req_detail, source)
                    save_ban_pick(match, req_detail)
                    get_info_results(match, req_detail)
                    save_performance(match, req_detail)
                    # break
            except Exception as e:
                logger.error('(offset={})Failed to request html HLTV: {}'.format(offset, str(e)))
                continue
            # break

        print("Process is was done...")
