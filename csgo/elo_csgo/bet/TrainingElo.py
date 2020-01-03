from .models import *

e = Player.objects.all()
p = Performance.objects.all()
count_player_id = len(e)
count_game = len(p)


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
    return abs(k * (ans - win_rate))


def diffEloPlayer(rating, ans, diff_elo, sum_rating):
    if ans == 1:
        return diff_elo * rating / sum_rating * 5
    else:
        return -diff_elo * sum_rating / (5 * rating)


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
    if expected_value_a < 0.05 and expected_value_b < 0.05:
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
    while count < count_game:
        count_update_elo = count

        while True:
            if count_update_elo > count + 12:
                break

            if count_update_elo > count_game - 1:
                break

            p[count_update_elo].elo = e[e_dict[p[count_update_elo].id_player]].elo
            count_update_elo += 1

        hs = 0
        hs1 = 0

        elo_a = 0.0
        for i in range(5):
            elo_a += p[count + i].elo

        if p[count].team == p[count + 5].team and p[count].match_id == p[count + 5].match_id:
            elo_a = (elo_a + p[count + 5].elo) / 6
            hs = 1
        else:
            elo_a /= 5

        elo_b = 0.0
        for i in range(5, 10):
            elo_b += p[count + i + hs].elo

        if count + 10 + hs < count_game and p[count + 5 + hs].team == p[count + 10 + hs].team and p[
            count + 5 + hs].match_id == p[count + 10 + hs].match_id:
            elo_b = (elo_b + p[count + 10 + hs].elo) / 6
            hs1 = 1
        else:
            elo_b /= 5

        sum_rating_a = 0.0
        for i in range(5):
            sum_rating_a += p[count + i].rating

        if hs == 1:
            sum_rating_a += p[count + 5].rating

        sum_rating_b = 0.0
        for i in range(5, 10):
            sum_rating_b += p[count + i + hs].rating

        if hs1 == 1:
            sum_rating_b += p[count + 10 + hs].rating

        w_a = winRate(elo_a, elo_b)
        diff_elo = diffElo(w_a, p[count].result, 25)
        for i in range(5):
            p[count + i].elo += diffEloPlayer(p[count + i].rating, p[count].result, diff_elo, sum_rating_a)
            p[count + (5 + i) + hs].elo += diffEloPlayer(p[count + (5 + i) + hs].rating, p[count + 5 + hs].result,
                                                         diff_elo, sum_rating_b)

        if hs == 1:
            p[count + 5].elo += diffEloPlayer(p[count + 5].rating, p[count].result, diff_elo, sum_rating_a)

        if hs1 == 1:
            p[count + 10 + hs].elo += diffEloPlayer(p[count + 10 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                    sum_rating_b)

        for i in range(10):
            update_elo(p[count + i].id_player, p[count + i].elo)

        if count + 10 < count_player_id:
            update_elo(p[count + 10].id_player, p[count + 10].elo)

        if count + 11 < count_player_id:
            update_elo(p[count + 11].id_player, p[count + 11].elo)

        count += 10 + hs1 + hs

    Player.objects.bulk_update(e, ['elo'])
