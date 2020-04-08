from .models import *
from datetime import timedelta, datetime
from .constant import day
from datetime import timedelta, datetime as my_datetime



import requests
e = Player.objects.all()
p1 = Performance.objects.all()
count_player_id = len(e)
hs = 35.0
q_hs = 450

def hash_map():
    tmp = {}
    for i in range(count_player_id):
        tmp.update({e[i].id_player: i})

    return tmp


e_dict = hash_map()


def update_elo(id_player, elo):
    for j in range(count_player_id):
        if id_player == e[j].id_player:
            e[j].elo = elo
            break


def winRate(elo_a, elo_b):
    """
    % thắng đội A
    :param elo_a:
    :param elo_b:
    :return: %
    """
    q_a = pow(10, elo_a / q_hs)
    q_b = pow(10, elo_b / q_hs)

    return q_a / (q_a + q_b)


def diffElo(win_rate, ans, k):
    # if elo <= 1600:
    #     k = 35
    # if elo > 1600 and elo <= 2000:
    #     k = 30
    # if elo > 2000 and elo <= 2400:
    #     k = 25
    # if elo > 2400:
    #     k = 20
    return abs(k * (ans - win_rate)*5)


def diffEloPlayer(rating, ans, diff_elo, sum_rating, sum_rating_nd):
    if ans == 1:
        return diff_elo * rating / sum_rating
    else:
        return -diff_elo / (sum_rating_nd * rating)


def expectedValue(w_a, bet_a):
    """
    # sự kỳ vọng khi chơi theo đội nào thì 1 đồng ăn bao nhiêu đồng (tiền lãi)
    :param w_a: win rate cua đội tính theo elo
    :param bet_a: tính tỷ lệ tiền lãi mang về so với 1 đồng (tiền lãi thôi)
    :return:
    """
    return w_a * bet_a - (1 - w_a) * 1


def according(expected_value_a, expected_value_b, bet_team_a, bet_team_b):
    if expected_value_a < 0 and expected_value_b < 0:
        return -1
    if expected_value_a > 0 and expected_value_b < 0:
        return 1
    if expected_value_a < 0 and expected_value_b > 0:
        return 0
    if expected_value_a > 0 and expected_value_b > 0:
        if bet_team_a < bet_team_b:
            return 1
        else:
            return 0



def edge(w_a, bet_a):
    """
    sự ăn thua với nhà cái
    :param w_a:
    :param bet_a:
    :return:
    """
    if w_a != 0:
        return (bet_a + 1) / (1 / w_a)
    return -1



def kelly(according, edge_a, edge_b, bet_a, bet_b):
    """
    đánh mỗi ván bao nhiêu tiền, bao nhiêu % với số tiền hiện tại
    :param according:
    :param edge_a:
    :param edge_b:
    :param bet_a:
    :param bet_b:
    :return:
    """
    if according == 1:
        return (edge_a - 1) / bet_a

    if according == 0:
        return (edge_b - 1) / bet_b

    return 0


def trainingEloPlayer():
    count = 0
    count_game = len(p1)
    # for i in range(count_player_id):
    #     e[i].elo = 1600
    for i in range(count_game):
        # p1[i].elo = 1600
        # p1[i].check = 0
        print(p1[1].elo)
        break
    p = sorted(p1, key=lambda Performance: Performance.time)
    # for i in range(count_game):
    #     p[i].elo = 1600
    #     p[i].check = 0
    while count < count_game:
        if p[count].check == 1:
            count += 1
            continue
        for i in range(10):
            for j in range(len(e)):
                if count+i < count_game and p[count+i].id_player == e[j].id_player:
                    p[count+i].elo = e[j].elo
                    break
        dem = 1
        for i in range(1, 15):
            if count + i < count_game and p[count].match_id == p[count + i].match_id and p[count].map == p[count + i].map:
                dem += 1
            else:
                break
        # print(dem, "baobao")
        if dem != 10:
            # print(p[count].match_id)
            for i in range(count, count + dem):
                if i < count_game:
                    p[i].check = 1
                    p[i].bet = 0
                    # p[i].save()
            count = count + dem
            # print(count)

        if dem == 10:
            elo_a = 0.0
            elo_b = 0.0
            sum_rating_a = 0.0
            sum_rating_b = 0.0
            sum_rating_a_nd = 0.0
            sum_rating_b_nd = 0.0
            for i in range(5):
                if count + i < count_game:
                    elo_a += p[count + i].elo/5
                    sum_rating_a += p[count + i].rating
                    sum_rating_a_nd += 1 / p[count + i].rating
            for i in range(5, 10):
                if count + i < count_game:
                    elo_b += p[count + i].elo/5
                    sum_rating_b += p[count + i].rating
                    sum_rating_b_nd += 1 / p[count + i].rating

            w_a = winRate(elo_a, elo_b)
            if p[count].result == 1:
                ans = 1.0
            else:
                ans = 0.0
            diff_elo_a = diffElo(w_a, ans, hs)
            diff_elo_b = diffElo(1.0-w_a, 1.0-ans, hs)
            print(p[count].match_id)

            for i in range(5):
                if count + i < count_game:
                    p[count + i].elo += diffEloPlayer(p[count + i].rating, ans, diff_elo_a, sum_rating_a, sum_rating_a_nd)
                    p[count + i].bet = w_a
            for i in range(5, 10):
                if count + i < count_game:
                    p[count + i].elo += diffEloPlayer(p[count + i].rating, 1.0-ans, diff_elo_b, sum_rating_b, sum_rating_b_nd)
                    p[count + i].bet = 1 - w_a
            for i in range(10):
                if count + i < count_game:
                    update_elo(p[count + i].id_player, p[count + i].elo)
            for i in range(count, count + 10):
                if i < count_game:
                    p[i].check = 1
                    # p[i].save()
            count += 10
    p2 = sorted(p, key=lambda Performance: Performance.id)
    p3 = Performance.objects.all()
    # for i in range(len(p3)):
    #     p3[i].check = 1
    for i in range(len(p3)):
        if p3[i].check == 0:
            print(p3[i].id)
            p3[i].elo = p2[i].elo
            p3[i].bet = p2[i].bet
            p3[i].check = 1
            p3[i].save()
    Player.objects.bulk_update(e, ['elo'])



def save_winrate():
    # map winrate vao match theo bogame
    match = Match.objects.all()
    p = Performance.objects.all()
    for i in range(len(p)):
        print(p[i].id)
        break
    for i in range(len(match)):
        print(match[i].id)
        break
    p1 = sorted(p, key=lambda Performance: Performance.time)
    bo_game = -1
    for i in range(len(p1)):
        if p1[i].match_id != bo_game:
            print(p1[i].match_id)
            bo_game = p1[i].match_id
            bo = 1
            if match[p1[i].match_id-1].type == "Best of 3":
                bo = 3
            if match[p1[i].match_id-1].type == "Best of 5":
                bo = 5
            n = p1[i].bet
            if bo == 3:
                match[p1[i].match_id - 1].w_a = 3 * n * n - 2 * n * n * n
            if bo == 5:
                match[p1[i].match_id - 1].w_a = 6 * pow(n, 5) - 15 * pow(n, 4) + 10 * pow(n, 3)

            else:
                match[p1[i].match_id - 1].w_a = n

            match[p1[i].match_id-1].w_a = p1[i].bet
            print(match[p1[i].match_id-1].w_a)
    Match.objects.bulk_update(match, ['w_a'])

    # map cái win rate tu Match sang mat_upcomming de tinh loi lai
    match_upcoming = MatchUpcoming.objects.all()
    for item in match_upcoming:
        print(item.id)
        t_now = item.time.strftime("%Y-%m-%d") + " 00:00:00"
        # print(t_now)
        time = datetime.strptime(t_now, '%Y-%m-%d %H:%M:%S')
        time_limit = time.replace(hour=23, minute=59, second=59) + 1 / 2 * timedelta(days=day)
        # print(time_limit)
        match = Match.objects.filter(time__range=(t_now, time_limit)).order_by('time')
        for x in match:
            if x.team_a == item.team_a and x.team_b == item.team_b:
                n = x.w_a
                item.winrate_a = n
                item.winrate_b = 1 - item.winrate_a
                item.match_id = x.id
                break
        ev_a_pin = expectedValue(item.winrate_a, item.bet_team_a - 1)
        ev_b_pin = expectedValue(1 - item.winrate_a, item.bet_team_b - 1)

        acd_a = according(ev_a_pin, ev_b_pin,  item.bet_team_a - 1, item.bet_team_b - 1)

        edge_a_p = edge(item.winrate_a, item.bet_team_a - 1)
        edge_b_p = edge(1 - item.winrate_a, item.bet_team_b - 1)

        kel_p = kelly(acd_a, edge_a_p, edge_b_p, item.bet_team_a - 1, item.bet_team_b - 1)

        if kel_p > 0:
            if acd_a == 1:
                item.suggestion_a = kel_p / 8
                item.suggestion_b = 0
            if acd_a == 0:
                item.suggestion_a = 0
                item.suggestion_b = kel_p / 8

        item.save()


def save_winrate_vp():
    match = Match.objects.all()
    match_upcoming = BetMatch.objects.all()
    # map winrate tu map sang bet mâp vpgame
    for item in match_upcoming:
        if item.match_id is not None:
            continue
        print(item.id)
        t_now = item.time.strftime("%Y-%m-%d") + " 00:00:00"
        # print(t_now)
        time = datetime.strptime(t_now, '%Y-%m-%d %H:%M:%S')
        time_limit = time.replace(hour=23, minute=59, second=59) + 1 / 2 * timedelta(days=day)
        # print(time_limit)
        match = Match.objects.filter(time__range=(t_now, time_limit)).order_by('time')
        for x in match:
            if x.team_a.lower() == item.team_a.lower() and x.team_b.lower() == item.team_b.lower():
                item.w_a = x.w_a
                item.match_id = x.id
                break
            if x.team_a.lower() == item.team_b.lower() and x.team_b.lower() == item.team_a.lower():
                item.w_a = 1 - x.w_a
                item.match_id = x.id
                break
        item.save()

def crawler_over_5etop():
    """
    function crawl data match upcoming 5etop
    :return:
    """
    s = 'https://www.5etop.com/api/match/list.do?status=end&page='
    s1 = '&game=csgo'
    # egame = BetMatchEGame.objects.all()
    for i in range(1, 5):
        s2 = s+str(i)+s1
        five_etop_url = s2
        r = requests.get(five_etop_url)
        if r.ok:
            data = r.json().get("datas").get("list")
            for item in data:
                try:
                    match = item.get("offerMatch")
                    time = int(match.get("time"))
                    time = my_datetime.fromtimestamp(time / 1000.0)

                    team_a = match.get("vs1").get("name")
                    team_b = match.get("vs2").get("name")

                    odds_team_a = match.get("vs1").get("odds")
                    odds_team_b = match.get("vs2").get("odds")

                    point_team_a = match.get("vs1").get("score")
                    point_team_b = match.get("vs2").get("score")

                    link = 'https://www.5etop.com/match/'+str(match.get("id"))+'/v2/show.do'
                    print(link)
                    # for x in egame:
                    #     if x.team_a == team_a and x.team_b == team_b and x.time == time:
                    #         x.source = link
                    #         x.save()
                    #         break

                    egame = BetMatchEGame.objects.filter(time=time, team_a=team_a, team_b=team_b)
                    if len(egame) > 0:
                        continue
                    BetMatchEGame.objects.create(
                        time=time,
                        team_a=team_a,
                        team_b=team_b,
                        bet_team_a=odds_team_a,
                        bet_team_b=odds_team_b,
                        point_team_a=point_team_a,
                        point_team_b=point_team_b,
                        source=link,
                    )



                except Exception as e:
                    print('5etop: {}'.format(str(e)))

def save_winrate_5e():
    match = Match.objects.all()
    match_upcoming = BetMatchEGame.objects.all()
    # map winrate tu map sang bet mâp vpgame
    for item in match_upcoming:
        if item.match_id is not None:
            continue
        print(item.id)
        t_now = item.time.strftime("%Y-%m-%d") + " 00:00:00"
        # print(t_now)
        time = datetime.strptime(t_now, '%Y-%m-%d %H:%M:%S')
        time_limit = time.replace(hour=23, minute=59, second=59) + 1 / 2 * timedelta(days=day)
        # print(time_limit)
        match = Match.objects.filter(time__range=(t_now, time_limit)).order_by('time')
        for x in match:
            if x.team_a.lower() == item.team_a.lower() and x.team_b.lower() == item.team_b.lower():
                item.w_a = x.w_a
                item.match_id = x.id
                break
            if x.team_a.lower() == item.team_b.lower() and x.team_b.lower() == item.team_a.lower():
                item.w_a = 1-x.w_a
                item.match_id = x.id
                break

        item.save()


def upcomming_vp(vp_api_link):
    r = requests.get(vp_api_link)
    if r.ok:
        data = r.json().get("data")
        for item in data:
            try:
                time = int(item.get("start_time"))
                time = my_datetime.fromtimestamp(time)

                team_a = item.get("teams").get("left").get("name")
                team_b = item.get("teams").get("right").get("name")

                match_winner = item.get("predictions")[0]
                odds_team_a = match_winner.get("option").get("left").get("odds")
                odds_team_b = match_winner.get("option").get("right").get("odds")

                type = item.get("round")

                id = item.get("predictions")[0]['id']

                link = 'https://www.vpgame.com/match/'+str(item.get("predictions")[0]['id'])+'.html'
                print(link)
                vpgame = MatchUpcomingVpgame.objects.filter(round_id=id).first()

                if vpgame:
                    MatchUpcomingVpgame.objects.update_or_create(
                        round_id=vpgame.round_id,
                        defaults={
                            'bet_team_a': odds_team_a,
                            'bet_team_b': odds_team_b,
                            'time': time,
                            'team_a': team_a,
                            'team_b': team_b,
                            'source': link,
                            'type': type,
                        }
                    )
                else:
                    MatchUpcomingVpgame.objects.create(
                        time=time,
                        team_a=team_a,
                        team_b=team_b,
                        bet_team_a=odds_team_a,
                        bet_team_b=odds_team_b,
                        source=link,
                        round_id=id,
                        type=type
                    )



            except Exception as e:
                print('upcomming vpgame: {}'.format(str(e)))


def upcomming_5etop():
    five_etop_url = 'https://www.5etop.com/api/match/list.do?status=run&game=csgo'
    r = requests.get(five_etop_url)
    if r.ok:
        data = r.json().get("datas").get("list")
        for item in data:
            try:
                match = item.get("offerMatch")
                time = int(match.get("time"))
                time = my_datetime.fromtimestamp(time / 1000.0)

                team_a = str(match.get("vs1").get("name"))
                team_b = str(match.get("vs2").get("name"))

                bet_team_a = float(match.get("vs1").get("odds"))
                bet_team_b = float(match.get("vs2").get("odds"))

                type = str(match.get("bo"))

                round_id = int(match.get("id"))
                link = 'https://www.5etop.com/match/'+str(match.get("id"))+'/v2/show.do'
                print(link,team_a,time,round_id)

                egame = MatchUpcomingegame.objects.filter(round_id=round_id).first()

                if egame:
                    MatchUpcomingegame.objects.update_or_create(
                        round_id=egame.round_id,
                        defaults={
                            'bet_team_a': bet_team_a,
                            'bet_team_b': bet_team_b,
                            'time': time,
                            'team_a': team_a,
                            'team_b': team_b,
                            'source': link,
                            'type': type,
                        }
                    )
                else:
                    MatchUpcomingegame.objects.create(
                        time=time,
                        team_a=team_a,
                        team_b=team_b,
                        bet_team_a=bet_team_a,
                        bet_team_b=bet_team_b,
                        source=link,
                        round_id=round_id,
                        type=type
                    )



            except Exception as e:
                print('5etop: {}'.format(str(e)))


def map_up_5e():
    match_upcoming = MatchUpcomingegame.objects.all()
    # map id tu upcoming hltv sang 5rtop
    for item in match_upcoming:
        if item.match_id is not None:
            continue
        print(item.id)
        t_now = item.time.strftime("%Y-%m-%d") + " 00:00:00"
        # print(t_now)
        time = datetime.strptime(t_now, '%Y-%m-%d %H:%M:%S')
        time_limit = time.replace(hour=23, minute=59, second=59) + 1 / 2 * timedelta(days=day)
        # print(time_limit)
        match = MatchUpcoming.objects.filter(time__range=(t_now, time_limit)).order_by('time')
        for x in match:
            if x.team_a.lower() == item.team_a.lower() and x.team_b.lower() == item.team_b.lower():
                item.match_id = x.id
                break
            if x.team_a.lower() == item.team_b.lower() and x.team_b.lower() == item.team_a.lower():
                item.match_id = x.id
                break

        item.save()

def map_up_vp():
    match_upcoming = MatchUpcomingVpgame.objects.all()
    # map id tu upcoming hltv sang 5rtop
    for item in match_upcoming:
        if item.match_id is not None:
            continue
        print(item.id)
        t_now = item.time.strftime("%Y-%m-%d") + " 00:00:00"
        # print(t_now)
        time = datetime.strptime(t_now, '%Y-%m-%d %H:%M:%S')
        time_limit = time.replace(hour=23, minute=59, second=59) + 1 / 2 * timedelta(days=day)
        # print(time_limit)
        match = MatchUpcoming.objects.filter(time__range=(t_now, time_limit)).order_by('time')
        for x in match:
            if x.team_a.lower() == item.team_a.lower() and x.team_b.lower() == item.team_b.lower():
                item.match_id = x.id
                break
            if x.team_a.lower() == item.team_b.lower() and x.team_b.lower() == item.team_a.lower():
                item.match_id = x.id
                break

        item.save()
