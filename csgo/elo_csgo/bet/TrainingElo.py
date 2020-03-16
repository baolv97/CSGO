from .models import *
from datetime import timedelta, datetime
from .constant import day
from operator import itemgetter, attrgetter, methodcaller
e = Player.objects.all()
p1 = Performance.objects.all()
count_player_id = len(e)


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
    q_a = pow(10, elo_a / 400)
    q_b = pow(10, elo_b / 400)

    return q_a / (q_a + q_b)


def diffElo(win_rate, ans, k):
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
    return  -1



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
    for i in range(count_player_id):
        e[i].elo = 1800
    for i in range(count_game):
        p1[i].elo = 1800
        p1[i].check = 0
    p = sorted(p1, key=lambda Performance: Performance.time)
    for i in range(count_game):
        p[i].elo = 1800
        p[i].check = 0
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
            diff_elo_a = diffElo(w_a, ans, 25.0)
            diff_elo_b = diffElo(1.0-w_a, 1.0-ans, 25.0)
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
    for i in range(len(p3)):
        if p3[i].check == 0:
            print(p3[i].id)
            p3[i].elo = p2[i].elo
            p3[i].bet = p2[i].bet
            p3[i].check = 1
            p3[i].save()
    Player.objects.bulk_update(e, ['elo'])



def save_winrate():
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
            match[p1[i].match_id-1].w_a = p1[i].bet
            print(match[p1[i].match_id-1].w_a)
    Match.objects.bulk_update(match, ['w_a'])

    # match_upcoming = MatchUpcoming.objects.all()
    # for item in match_upcoming:
    #     print(item.id)
    #     t_now = item.time.strftime("%Y-%m-%d") + " 00:00:00"
    #     # print(t_now)
    #     time = datetime.strptime(t_now, '%Y-%m-%d %H:%M:%S')
    #     time_limit = time.replace(hour=23, minute=59, second=59) + 1 / 2 * timedelta(days=day)
    #     # print(time_limit)
    #     match = Match.objects.filter(time__range=(t_now, time_limit)).order_by('time')
    #     for x in match:
    #         if x.team_a == item.team_a and x.team_b == item.team_b:
    #             item.winrate_a = x.w_a
    #             item.winrate_b = 1-x.w_a
    #             # item.save()
    #             break
    #     ev_a_pin = expectedValue(item.winrate_a, item.bet_team_a - 1)
    #     ev_b_pin = expectedValue(1 - item.winrate_a, item.bet_team_b - 1)
    #
    #     acd_a = according(ev_a_pin, ev_b_pin,  item.bet_team_a - 1, item.bet_team_b - 1)
    #
    #     edge_a_p = edge(item.winrate_a, item.bet_team_a - 1)
    #     edge_b_p = edge(1 - item.winrate_a, item.bet_team_b - 1)
    #
    #     kel_p = kelly(acd_a, edge_a_p, edge_b_p, item.bet_team_a - 1, item.bet_team_b - 1)
    #
    #     if kel_p > 0:
    #         if acd_a == 1:
    #             item.suggestion_a = kel_p / 8
    #             item.suggestion_b = 0
    #         if acd_a == 0:
    #             item.suggestion_a = 0
    #             item.suggestion_b = kel_p / 8
    #
    #     item.save()
