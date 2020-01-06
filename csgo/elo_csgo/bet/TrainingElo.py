from .models import *

e = Player.objects.all()
p = Performance.objects.all()
count_player_id = len(e)


def hash_map():
    tmp = {}
    for i in range(count_player_id):
        tmp.update({e[i].id_player: i})

    return tmp


e_dict = hash_map()


def update_elo(id_player, elo):
    e[e_dict[id_player]].elo = elo


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
    return abs(k * (ans - win_rate))*5


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


def according(expected_value_a, expected_value_b):
    """
    hàm quyết định thoe đội nào dựa vào expected_Value
    :param expected_value_a:
    :param expected_value_b:
    :return:
    """
    if expected_value_a < 0 and expected_value_b < 0:
        return -1

    if expected_value_a > expected_value_b:
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
    return (bet_a + 1) / (1 / w_a)


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
    count_game = len(p)
    for i in range(count_player_id):
        e[i].elo = 1800
    for i in range(count_game):
        p[i].elo = 1800

    while count < count_game-1:
        for i in range(10):
            if count + i < count_game:
                p[count+i].elo = e[e_dict[p[count + i].id_player]].elo

        hs = 1
        hs1 = 1

        if count + 5 < count_game and p[count].team == p[count + 5].team and p[count].match_id == p[count + 5].match_id:
            hs = 1
        else:
            hs = 0

        if count+10+hs < count_game and p[count + 5 + hs].team == p[count + 5 + 5 + hs].team and p[count + 5 + hs].match_id == p[count + 5 + 5 + hs].match_id:
            hs1 = 1
        else:
            hs1 = 0

        if hs == 1 or hs1 == 1:
            count += 10 + hs + hs1

        if hs == 0 or hs1 == 0:
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

            diff_elo_a = diffElo(w_a, p[count].result, 25)
            diff_elo_b = diffElo(1-w_a, 1-p[count].result, 25)

            for i in range(5):
                if count + i < count_game:
                    p[count + i].elo += diffEloPlayer(p[count + i].rating, p[count].result, diff_elo_a, sum_rating_a, sum_rating_a_nd)
            for i in range(5, 10):
                if count + i < count_game:
                    p[count + i].elo += diffEloPlayer(p[count + i].rating, 1-p[count].result, diff_elo_b, sum_rating_b, sum_rating_b_nd)

            for i in range(10):
                if count + i < count_game:
                    update_elo(p[count + i].id_player, p[count + i].elo)

            count += 10

    Player.objects.bulk_update(e, ['elo'])


