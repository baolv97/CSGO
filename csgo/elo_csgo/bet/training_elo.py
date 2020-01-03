from .models import *

e = Player.objects.all()
p = Performance.objects.all()




def update_elo(id_player, elo):
    for i in range(len(e)):
        if e[i].id_player == id_player:
            e[i].elo = elo
            # e[i].save()
            break


def winRate(elo_a, elo_b):
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
    return w_a * bet_a - (1 - w_a) * 1


def according(expected_value_a, expected_value_b):
    if expected_value_a < 0.05 and expected_value_b < 0.05:
        return -1

    if expected_value_a > expected_value_b:
        return 1
    else:
        return 0


def edge(w_a, bet_a):
    return (bet_a + 1) / (1 / w_a)


def kelly(according, edge_a, edge_b, bet_a, bet_b):
    if according == 1:
        return (edge_a - 1) / bet_a

    if according == 0:
        return (edge_b - 1) / bet_b

    return 0


def trainingEloPlayer():
    count = 0
    # e = Player.objects.all()
    # p = Performance.objects.all()
    count_player_id = len(e)
    count_game = len(p)

    while count < count_game:
        count_update_elo = count

        while True:
            if count_update_elo > count + 12:
                break
            if count_update_elo > count_game - 1:
                break
            for i in range(count_player_id):
                if p[count_update_elo].id_player == e[i].id_player:
                    p[count_update_elo].elo = e[i].elo
                    break

            count_update_elo += 1

        elo_a = 0.0
        elo_b = 0.0
        hs = 0
        hs1 = 0

        if p[count].team == p[count + 5].team and p[count].match_id == p[count + 5].match_id:
            elo_a = (p[count].elo + p[count + 1].elo + p[count + 2].elo + p[count + 3].elo + p[count + 4].elo + p[
                count + 5].elo) / 6
            hs = 1
        else:
            elo_a = (p[count].elo + p[count + 1].elo + p[count + 2].elo + p[count + 3].elo + p[count + 4].elo) / 5

        if count + 10 + hs < count_game and p[count + 5 + hs].team == p[count + 10 + hs].team and p[
            count + 5 + hs].match_id == p[count + 10 + hs].match_id:
            elo_b = (p[count + 5 + hs].elo + p[count + 6 + hs].elo + p[count + 7 + hs].elo + p[count + 8 + hs].elo + p[
                count + 9 + hs].elo + p[count + 10 + hs].elo) / 6
            hs1 = 1
        else:
            elo_b = (p[count + 5 + hs].elo + p[count + 6 + hs].elo + p[count + 7 + hs].elo + p[count + 8 + hs].elo + p[
                count + 9 + hs].elo) / 5

        sum_rating_a = 0.0
        sum_rating_b = 0.0

        if hs == 1:
            sum_rating_a = p[count].rating + p[count + 1].rating + p[count + 2].rating + p[count + 3].rating + p[
                count + 4].rating + p[count + 5].rating
        else:
            sum_rating_a = p[count].rating + p[count + 1].rating + p[count + 2].rating + p[count + 3].rating + p[
                count + 4].rating

        if hs1 == 1:
            sum_rating_b = p[count + 5 + hs].rating + p[count + 6 + hs].rating + p[count + 7 + hs].rating + p[
                count + 8 + hs].rating + p[count + 9 + hs].rating + p[count + 10 + hs].rating
        else:
            sum_rating_b = p[count + 5 + hs].rating + p[count + 6 + hs].rating + p[count + 7 + hs].rating + p[
                count + 8 + hs].rating + p[count + 9 + hs].rating

        w_a = winRate(elo_a, elo_b)

        print(p[count].match_id)

        diff_elo = diffElo(w_a, p[count].result, 25)

        p[count].elo += diffEloPlayer(p[count].rating, p[count].result, diff_elo, sum_rating_a)
        p[count + 1].elo += diffEloPlayer(p[count + 1].rating, p[count].result, diff_elo, sum_rating_a)
        p[count + 2].elo += diffEloPlayer(p[count + 2].rating, p[count].result, diff_elo, sum_rating_a)
        p[count + 3].elo += diffEloPlayer(p[count + 3].rating, p[count].result, diff_elo, sum_rating_a)
        p[count + 4].elo += diffEloPlayer(p[count + 4].rating, p[count].result, diff_elo, sum_rating_a)

        if hs == 1:
            p[count + 5].elo += diffEloPlayer(p[count + 5].rating, p[count].result, diff_elo, sum_rating_a)
            p[count + 5 + hs].elo += diffEloPlayer(p[count + 5 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)
            p[count + 6 + hs].elo += diffEloPlayer(p[count + 6 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)
            p[count + 7 + hs].elo += diffEloPlayer(p[count + 7 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)
            p[count + 8 + hs].elo += diffEloPlayer(p[count + 8 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)
            p[count + 9 + hs].elo += diffEloPlayer(p[count + 9 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)

            if hs1 == 1:
                p[count + 10 + hs].elo += diffEloPlayer(p[count + 10 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                        sum_rating_b)
        else:
            p[count + 5 + hs].elo += diffEloPlayer(p[count + 5 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)
            p[count + 6 + hs].elo += diffEloPlayer(p[count + 6 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)
            p[count + 7 + hs].elo += diffEloPlayer(p[count + 7 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)
            p[count + 8 + hs].elo += diffEloPlayer(p[count + 8 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)
            p[count + 9 + hs].elo += diffEloPlayer(p[count + 9 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                   sum_rating_b)
            if hs1 == 1:
                p[count + 10 + hs].elo += diffEloPlayer(p[count + 10 + hs].rating, p[count + 5 + hs].result, diff_elo,
                                                        sum_rating_b)

        update_elo(p[count].id_player, p[count].elo)
        update_elo(p[count + 1].id_player, p[count + 1].elo)
        update_elo(p[count + 2].id_player, p[count + 2].elo)
        update_elo(p[count + 3].id_player, p[count + 3].elo)
        update_elo(p[count + 4].id_player, p[count + 4].elo)

        update_elo(p[count + 5].id_player, p[count + 5].elo)
        update_elo(p[count + 6].id_player, p[count + 6].elo)
        update_elo(p[count + 7].id_player, p[count + 7].elo)
        update_elo(p[count + 8].id_player, p[count + 8].elo)
        update_elo(p[count + 9].id_player, p[count + 9].elo)
        if count + 10 < count_player_id:
            update_elo(p[count + 10].id_player, p[count + 10].elo)

        if count + 11 < count_player_id:
            update_elo(p[count + 11].id_player, p[count + 11].elo)

        count += 10 + hs1 + hs

    Player.objects.bulk_update(e, ['elo'])
