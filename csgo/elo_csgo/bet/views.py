# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import BetUpcoming, MatchUpcoming
from datetime import timedelta, datetime
from .constant import day, pinnacle, five_etop, vp_game
from django.core.management import call_command
from .models import *
import os
import subprocess
from .forms import crawl_upcomming, crawl_upcomming_vp
from .TrainingElo import save_winrate_vp,map_up_vp, crawler_over_5etop, save_winrate_5e, upcomming_vp, upcomming_5etop,map_up_5e
brankroll = 10000.0
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/bet/')
    return HttpResponseRedirect('/login/')

def takeSecond(elem):
    return elem[3]


def check_today(time):
    t_now = datetime.now()
    return t_now.day == time.day and t_now.month == time.month and t_now.year == time.year


def refresh(request):
    # call_command('crawler_9_train_elo_for_player')
    call_command('crawler_10_match_upcoming')
    # import time
    # time.sleep(20)
    return HttpResponse(1, content_type='application/json')


def crawlmatch(request):

    call_command('crawler_1_cs_go')
    result = 'Done crawl match - click add list player'
    context = {
        "result": result
    }

    return render(request, 'bet/training.html', context)

def listplayer(request):
    result = 'null'
    call_command('crawler_6_get_list_player')
    result = 'Done Get new Player - click result match'
    context = {
        "result": result
    }

    return render(request, 'bet/training.html', context)


def resultmatch(request):
    call_command('crawler_7_add_column_result')
    result = 'Done Result match - click Add bet macth'
    context = {
        "result": result
    }

    return render(request, 'bet/training.html', context)


def mapbet(request):
    call_command('crawler_8_add_column_bet_for_performance')
    # call_command('crawler_9_train_elo_for_player')
    result = 'Done Map bet match - click Refresh ELO'
    context = {
        "result": result
    }

    return render(request, 'bet/training.html', context)

def refreshELO(request):
    # call_command('crawler_8_add_column_bet_for_performance')
    call_command('crawler_9_train_elo_for_player')
    result = 'Done Training ELO'
    context = {
        "result": result
    }

    return render(request, 'bet/training.html', context)


def training_elo(request):
    result = 'click crawlmatch'
    context = {
        "result": result
    }

    return render(request, 'bet/training.html', context)


def refresh_over(request):
    return HttpResponse(1, content_type='application/json')


def winRate(elo_a, elo_b):
    q_a = pow(10, elo_a / 400)
    q_b = pow(10, elo_b / 400)

    return q_a / (q_a + q_b)


def expectedValue(w_a, bet_a):
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
    return (bet_a + 1) / (1 / w_a)


def kelly(according, edge_a, edge_b, bet_a, bet_b):
    if according == 1:
        return (edge_a - 1) / bet_a

    if according == 0:
        return (edge_b - 1) / bet_b

    return 0


def detail(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    # set limit time for query: in 2 next day
    t_now = datetime.now()
    time_limit = datetime.now().replace(hour=23, minute=59, second=59) + timedelta(days=day)
    print(time_limit)
    # get matches in 2 next day, oder_by time
    matches = MatchUpcoming.objects.filter(time__range=(t_now, time_limit)).order_by('time')
    matches_all = MatchUpcoming.objects.all()
    for i in range(len(matches_all)):
        break
    result = []
    e = Player.objects.all()
    for item in matches:
        # get odds of banker
        bets = BetUpcoming.objects.filter(match_id=item.id)
        # if bets.count() == 0:
        #     # if match have no bet -> continue
        #     # else append bet to result
        #     continue
        # get total elo team_a and team_b
        total_elo_a = 0
        total_elo_b = 0
        d_team_a = 0
        d_team_b = 0
        players = MatchUpcomingPlayer.objects.filter(match_upcoming=item)
        for p in players:
            player = Player.objects.filter(name=p.name)
            if player.count() > 1:
                player = player.filter(id_player=p.id_player)
            player = player.first()
            player_elo = player.elo if player else 1800

            if p.team == item.team_a:
                total_elo_a += player_elo
                # print(p.team, p.name, player_elo)
                d_team_a += 1
            else:
                total_elo_b += player_elo
                # print(p.team, p.name, player_elo)
                d_team_b += 1
        # print("total_elo team A", total_elo_a)
        # print("total_elo team B", total_elo_b)
        # print("nguoi A", d_team_a)
        # print("nguoi B", d_team_b)
        if d_team_a != 0 and d_team_b !=0:
            elo_a = total_elo_a / d_team_a
            elo_b = total_elo_b / d_team_b
        else:
            elo_a = 0
            elo_b = 0

        w_a = winRate(elo_a, elo_b)
        bo = 1
        if item.type == "Best of 3":
            bo = 3
        if item.type == "Best of 5":
            bo = 5
        n = w_a
        if bo == 3:
            w_a = 3 * n * n - 2 * n * n * n
        if bo == 5:
            w_a = 6 * pow(n, 5) - 15 * pow(n, 4) + 10 * pow(n, 3)
        print(n, w_a, bo, "test")
        w_b = 1-w_a
        # print("win rate team A", w_a)
        # print("win rate team B", w_b)
        # set up suggestion nha cai pin
        pin_odds_team_a = 0.0
        pin_odds_team_b = 0.0
        vp_odds_team_a = 0.0
        vp_odds_team_b = 0.0
        etop_odds_team_a = 0.0
        etop_odds_team_b = 0.0
        for bet in bets:
            if bet.banker == pinnacle:
                pin_odds_team_a = bet.bet_team_a
                pin_odds_team_b = bet.bet_team_b
            if bet.banker == vp_game:
                vp_odds_team_a = bet.bet_team_a
                vp_odds_team_b = bet.bet_team_b
            if bet.banker == five_etop:
                etop_odds_team_a = bet.bet_team_a
                etop_odds_team_b = bet.bet_team_b
        # print("pin ", pin_odds_team_a)
        # print("pin ", pin_odds_team_b)

        egame = MatchUpcomingegame.objects.filter(match_id=item.id).first()

        if egame:
            link_egame = egame.source
            if egame.team_a == item.team_a:
                etop_odds_team_a = egame.bet_team_a
                etop_odds_team_b = egame.bet_team_b
            else:
                etop_odds_team_a = egame.bet_team_b
                etop_odds_team_b = egame.bet_team_a
        else:
            link_egame = item.source
            etop_odds_team_a = 0.0
            etop_odds_team_b = 0.0

        vpgame = MatchUpcomingVpgame.objects.filter(match_id=item.id).first()

        if vpgame:
            link_vp = vpgame.source
            if vpgame.team_a == item.team_a:
                vp_odds_team_a = vpgame.bet_team_a
                vp_odds_team_b = vpgame.bet_team_b
            else:
                vp_odds_team_a = vpgame.bet_team_b
                vp_odds_team_b = vpgame.bet_team_a
        else:
            link_vp = item.source
            vp_odds_team_a = 0.0
            vp_odds_team_b = 0.0


        # set up suggestion nha cai pin
        ev_a_pin = expectedValue(w_a, pin_odds_team_a - 1)
        ev_b_pin = expectedValue(w_b, pin_odds_team_b - 1)

        acd_a = according(ev_a_pin, ev_b_pin, pin_odds_team_a - 1,  pin_odds_team_b - 1)

        edge_a_p = edge(w_a, pin_odds_team_a - 1)
        edge_b_p = edge(w_b, pin_odds_team_b - 1)

        kel_p = kelly(acd_a, edge_a_p, edge_b_p, pin_odds_team_a - 1, pin_odds_team_b - 1)
        # print("pin ev ", ev_a_pin)
        # print("pin ev ", ev_b_pin)
        # print("pin acd ", acd_a)
        # print("pin edg ", edge_a_p)
        # print("pin edg ", edge_b_p)
        # print("pin kel ", kel_p / 16)
        kelly_a_p = 0
        kelly_b_p = 0

        if kel_p > 0:
            if acd_a == 1:
                kelly_a_p = kel_p / 16
                kelly_b_p = 0
            if acd_a == 0:
                kelly_a_p = 0
                kelly_b_p = kel_p / 16
        matches_all[item.id-1].bet_team_a = pin_odds_team_a
        matches_all[item.id-1].bet_team_b = pin_odds_team_b
        matches_all[item.id-1].suggestion_a = kelly_a_p
        matches_all[item.id-1].suggestion_b = kelly_b_p
        # print("baobao", matches_all[item.id-1].bet_team_a, pin_odds_team_a)
        # set up suggestion nha cai 5etop
        ev_a_e = expectedValue(w_a, etop_odds_team_a)
        ev_b_e = expectedValue(w_b, etop_odds_team_b)

        acd_a_e = according(ev_a_e, ev_b_e, etop_odds_team_a, etop_odds_team_b)

        edge_a_e = edge(w_a, etop_odds_team_a)
        edge_b_e = edge(w_b, etop_odds_team_b)

        kel_e = kelly(acd_a_e, edge_a_e, edge_b_e, etop_odds_team_a, etop_odds_team_b)

        kelly_a_e = 0
        kelly_b_e = 0
        # print("5e ev ", ev_a_e)
        # print("5e ev ", ev_b_e)
        # print("5e acd ", acd_a_e)
        # print("5e edg ", edge_a_e)
        # print("5e edg ", edge_b_e)
        # print("5e kel ", kel_e / 16)

        if kel_e > 0:
            if acd_a == 1:
                kelly_a_e = kel_e / 16
                kelly_b_e = 0
            if acd_a == 0:
                kelly_a_e = 0
                kelly_b_e = kel_e / 16
        matches_all[item.id-1].bet_team_a_e = etop_odds_team_a
        matches_all[item.id-1].bet_team_b_e = etop_odds_team_b
        matches_all[item.id-1].suggestion_a_e = kelly_a_e
        matches_all[item.id-1].suggestion_b_e = kelly_b_e
        matches_all[item.id-1].winrate_a = w_a
        matches_all[item.id-1].winrate_b = w_b
        matches_all[item.id-1].save()
        # set up suggestion nha cai vp
        ev_a_vp = expectedValue(w_a, vp_odds_team_a)
        ev_b_vp = expectedValue(w_b, vp_odds_team_b)

        acd_a_vp = according(ev_a_vp, ev_b_vp, vp_odds_team_a, vp_odds_team_b)

        edge_a_vp = edge(w_a, vp_odds_team_a)
        edge_b_vp = edge(w_b, vp_odds_team_b)

        kel_vp = kelly(acd_a_vp, edge_a_vp, edge_b_vp, vp_odds_team_a, vp_odds_team_b)
        # print("pin ev ", ev_a_pin)
        # print("pin ev ", ev_b_pin)
        # print("pin acd ", acd_a)
        # print("pin edg ", edge_a_p)
        # print("pin edg ", edge_b_p)
        # print("pin kel ", kel_p / 16)
        kelly_a_vp = 0
        kelly_b_vp = 0

        if kel_vp > 0:
            if acd_a_vp == 1:
                kelly_a_vp = kel_vp / 16
                kelly_b_vp = 0
            if acd_a_vp == 0:
                kelly_a_vp = 0
                kelly_b_vp = kel_vp / 16
        result.append({
            "date": "Today" if check_today(item.time) else item.time.strftime("%d/%m/%Y"),
            "time": item.time.strftime("%H:%M"),
            "source": item.source,
            "source_vp": link_vp,
            "source_egame": link_egame,
            "a": 1,
            "team_a": item.team_a,
            "team_b": item.team_b,

            "vp_odds_team_a": str(round(vp_odds_team_a+1, 2)),
            "vp_suggestion_team_a": str(round(kelly_a_vp * brankroll, 2)),
            "vp_odds_team_b": str(round(vp_odds_team_b+1, 2)),
            "vp_suggestion_team_b": str(round(kelly_b_vp * brankroll, 2)),

            "5e_odds_team_a": str(round(etop_odds_team_a+1, 2)),
            "5e_suggestion_team_a": str(round(kelly_a_e * brankroll, 2)),
            "5e_odds_team_b": str(round(etop_odds_team_b+1, 2)),
            "5e_suggestion_team_b": str(round(kelly_b_e * brankroll, 2)),

            "pin_odds_team_a": str(pin_odds_team_a),
            "pin_suggestion_team_a": str(round(kelly_a_p * brankroll, 2)),
            "pin_odds_team_b": str(pin_odds_team_b),
            "pin_suggestion_team_b": str(round(kelly_b_p * brankroll, 2)),

            "manual_odds_team_a": str(round(1 / w_a, 2)),
            "manual_suggestion_team_a": "-",
            "manual_odds_team_b": str(round(1 / w_b, 2)),
            "manual_suggestion_team_b": "-",
        })

    context = {
        "result": result
    }

    return render(request, 'bet/index.html', context)



def detail1(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    t_now = datetime.now()
    time_limit = datetime.now().replace(hour=23, minute=59, second=59) - timedelta(days=day)
    print(time_limit)
    matches_all = MatchUpcoming.objects.filter(time__range=(time_limit, t_now)).order_by('time')
    print(len(matches_all))
    result = []
    money = 10000
    pin_money = 0.0
    vp_money = 0.0
    for item in matches_all:
        # if item.match_id and item.winrate_a > 0 and item.winrate_b > 0:
        #     pin_result_a = 0.0
        #     pin_result_b = 0.0
        #     match = Match.objects.filter(id=item.match_id)
        #     ans = -1
        #     for x in match:
        #         if x.point_team_a - x.point_team_b > 0:
        #             ans = 1
        #         if x.point_team_b - x.point_team_a > 0:
        #             ans = 0
        #         break
        #     if ans == 1 and item.suggestion_a > 0:
        #         pin_money += item.suggestion_a * money * (item.bet_team_a - 1)
        #         pin_result_a = item.suggestion_a * money * (item.bet_team_a - 1)
        #     if ans == 1 and item.suggestion_a == 0:
        #         pin_money -= item.suggestion_b * money
        #         pin_result_b = -item.suggestion_b * money
        #     if ans == 0 and item.suggestion_a > 0:
        #         pin_money -= item.suggestion_a * money
        #         pin_result_a = -item.suggestion_a * money
        #     if ans == 0 and item.suggestion_a == 0:
        #         pin_money += item.suggestion_b * money * (item.bet_team_b - 1)
        #         pin_result_b = item.suggestion_b * money * (item.bet_team_b - 1)

        result.append({
                "date": item.time.strftime("%d/%m/%Y"),
                "time": item.time.strftime("%H:%M"),
                "source": item.source,
                "a": 1,
                "team_a": item.team_a,
                "team_b": item.team_b,

                "vp_odds_team_a": 0.0,
                "vp_suggestion_team_a": "-",
                "vp_odds_team_b": 0.0,
                "vp_suggestion_team_b": "-",

                "5e_odds_team_a": str(item.bet_team_a_e),
                "5e_suggestion_team_a": str(round(item.suggestion_a_e * brankroll, 2)),
                "5e_odds_team_b": str(item.bet_team_b_e),
                "5e_suggestion_team_b": str(round(item.suggestion_b_e * brankroll, 2)),

                "pin_odds_team_a": str(item.bet_team_a),
                "pin_suggestion_team_a": str(round(item.suggestion_a * brankroll, 2)),
                "pin_odds_team_b": str(item.bet_team_b),
                "pin_suggestion_team_b": str(round(item.suggestion_b * brankroll, 2)),

                "manual_odds_team_a": str(round(1/item.winrate_a, 2)),
                "manual_suggestion_team_a": 0,
                "manual_odds_team_b": str(round(1/item.winrate_b, 2)),
                "manual_suggestion_team_b": 0,

                "money_team_a": 0,
                "revenue_team_a": str(round(pin_money, 2)),
                "money_team_b": 0,
                "revenue_team_b": str(round(pin_money, 2)),
            })

    result.reverse()

    context = {
        "result": result
    }

    return render(request, 'bet/index.html', context)

def eloplayer(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    players = Player.objects.all()
    for i in range(len(players)):
        print(players[i].elo)
        break
    players = sorted(players, key=lambda Player: Player.elo, reverse=True)
    result = []
    for item in players:
        result.append({
            "id": item.id,
            "team": item.team,
            "id_game": item.id_player,
            "name": item.name,
            "elo": item.elo,
        })

    context = {
        "result": result
    }

    return render(request, 'bet/eloPlayer.html', context)

class perfor:
    def __init__(self, id, team, player, time, elo):
        self.id = id
        self.team = team
        self.player = player
        self.time = time
        self.elo = elo


def listperformance(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    p = Performance.objects.all()
    count_game = len(p)
    for i in range(count_game):
        p[i].check = 0
        break
    p = sorted(p, key=lambda Performance: Performance.time)
    result = []
    i = 0
    for item in p:
        result.append(
            # {
            # "id": item.id,
            # "team": item.team,
            # "player": item.player,
            # "time": item.time,
            # "elo": item.elo
            # }
            perfor(item.match_id, item.team, item.player, item.time, item.elo)
            )
        i += 1
        if i > 10000:
            break
    print(result)
    # result = sorted(result, key=lambda perfor: perfor.time)
    # result.sort(key=result.time)
    context = {
        "result": result
    }

    return render(request, 'bet/performance.html', context)

def vpgame(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    save_winrate_vp()
    result = []
    match_upcoming1 = BetMatch.objects.all()
    total = 0.0
    money = 10000
    match_upcoming = sorted(match_upcoming1, key=lambda BetMatch: BetMatch.time)
    end_time1 = "2019-11-01"
    time1 = datetime.strptime(end_time1, "%Y-%m-%d")
    for item in match_upcoming:
        if item.time < time1:
            continue
        if item.match_id is None:
            winA= 0
            winB=0
            if item.w_a > 0 and item.w_a < 1:
                winA= 1/item.w_a
                winB= 1/(1-item.w_a)
            result.append({
                "date": "Today" if check_today(item.time) else item.time.strftime("%d/%m/%Y"),
                "time": item.time.strftime("%H:%M"),
                "source": item.source,
                "a": 1,
                "team_a": item.team_a,
                "team_b": item.team_b,

                "vp_odds_team_a": item.bet_team_a + 1,
                "vp_suggestion_team_a": '-',
                "vp_odds_team_b": item.bet_team_b + 1,
                "vp_suggestion_team_b": '-',

                "manual_odds_team_a": str(round(winA, 2)),
                "manual_suggestion_team_a": '-',
                "manual_odds_team_b": str(round(winB, 2)),
                "manual_suggestion_team_b": '-',

                "money_team_a": '-',
                "revenue_team_a": str(round(total, 2)),
                "money_team_b": '-',
                "revenue_team_b": str(round(total, 2)),
            })
            continue
        if item.point_team_a - item.point_team_b > 0:
            ans = 1
        if item.point_team_b - item.point_team_a > 0:
            ans = 0
        if item.point_team_b - item.point_team_a == 0:
            ans = -1
        kel_p = -1
        acd_a = -1
        if item.w_a > 0 and item.w_a < 1:
            ev_a = expectedValue(item.w_a, item.bet_team_a)
            ev_b = expectedValue(1 - item.w_a, item.bet_team_b)

            acd_a = according(ev_a, ev_b, item.bet_team_a, item.bet_team_b)

            edge_a_p = edge(item.w_a, item.bet_team_a)
            edge_b_p = edge(1 - item.w_a, item.bet_team_b)

            kel_p = kelly(acd_a, edge_a_p, edge_b_p, item.bet_team_a, item.bet_team_b)
            suggestion_a = 0.0
            suggestion_b = 0.0
            money_odds_a = 0.0
            money_odds_b = 0.0
            if kel_p > 0:
                if acd_a == 1:
                    suggestion_a = kel_p / 16
                    suggestion_b = 0
                if acd_a == 0:
                    suggestion_a = 0
                    suggestion_b = kel_p / 16
            if ans == 1 and acd_a == 1:
                total += suggestion_a * money * item.bet_team_a
                money_odds_a = suggestion_a * money * item.bet_team_a
            if ans == 1 and acd_a == 0:
                total -= suggestion_b * money
                money_odds_b = -suggestion_b * money
            if ans == 0 and acd_a == 1:
                total -= suggestion_a * money
                money_odds_a = -suggestion_a * money
            if ans == 0 and acd_a == 0:
                total += suggestion_b * money * item.bet_team_b
                money_odds_b = suggestion_b * money * item.bet_team_b
            result.append({
                "date": "Today" if check_today(item.time) else item.time.strftime("%d/%m/%Y"),
                "time": item.time.strftime("%H:%M"),
                "source": item.source,
                "a": 1,
                "team_a": item.team_a,
                "team_b": item.team_b,

                "vp_odds_team_a": item.bet_team_a+1,
                "vp_suggestion_team_a": suggestion_a * money,
                "vp_odds_team_b": item.bet_team_b+1,
                "vp_suggestion_team_b": suggestion_b * money,


                "manual_odds_team_a": str(round(1 / item.w_a, 2)),
                "manual_suggestion_team_a": ans,
                "manual_odds_team_b": str(round(1 / (1 - item.w_a), 2)),
                "manual_suggestion_team_b": 1-ans,

                "money_team_a": str(round(money_odds_a, 2)),
                "revenue_team_a": str(round(total, 2)),
                "money_team_b": str(round(money_odds_b, 2)),
                "revenue_team_b": str(round(total, 2)),
            })

    result.reverse()
    context = {
        "result": result
    }

    return render(request, 'bet/vpgame.html', context)

# def changeodds_pin(request):
#     t_now = datetime.now()
#     end_time = "2019-02-13 11:34:37.710300"
#     end_time1 = "2020-03-18"
#     time1 = datetime.strptime(end_time1, "%Y-%m-%d")
#     matches_all = MatchUpcoming.objects.filter(time__range=(end_time, t_now)).order_by('time')
#     result = []
#     total = 0.0
#     money = 10000
#     for i in range(len(matches_all)):
#         if matches_all[i].winrate_a == 0:
#             continue
#         # if matches_all[i].time < time1:
#         #     continue
#         check = 0
#         for j in range(i):
#             if matches_all[i].time == matches_all[j].time and matches_all[i].team_a == matches_all[j].team_a and \
#                     matches_all[i].team_b == matches_all[j].team_b:
#                 check = 1
#                 break
#         if check == 1:
#             continue
#
#         # map cai result cua cac game
#         t_now = matches_all[i].time.strftime("%Y-%m-%d") + " 00:00:00"
#         # print(t_now)
#         time = datetime.strptime(t_now, '%Y-%m-%d %H:%M:%S')
#         time_limit = time.replace(hour=23, minute=59, second=59) + 1 / 2 * timedelta(days=day)
#         # print(time_limit)
#         match = Match.objects.filter(time__range=(t_now, time_limit)).order_by('time')
#         money_odds_a = 0.0
#         money_odds_b = 0.0
#         for x in match:
#             if x.team_a == matches_all[i].team_a and x.team_b == matches_all[i].team_b:
#                 if x.point_team_a - x.point_team_b > 0:
#                     ans = 1
#                 if x.point_team_a - x.point_team_b < 0:
#                     ans = 0
#                 break
#         bet_team_a = 0.0
#         bet_team_b = 0.0
#         if matches_all[i].bet_team_a > 0 and matches_all[i].bet_team_b > 0:
#             bet_team_a = (matches_all[i].bet_team_a + matches_all[i].bet_team_b) / matches_all[i].bet_team_b
#             bet_team_b = (matches_all[i].bet_team_a + matches_all[i].bet_team_b) / matches_all[i].bet_team_a
#         if matches_all[i].winrate_a > 0 and matches_all[i].winrate_b > 0:
#             ev_a = expectedValue(matches_all[i].winrate_a, bet_team_a - 1)
#             ev_b = expectedValue(1 - matches_all[i].winrate_a,  bet_team_b - 1)
#
#             acd_a = according(ev_a, ev_b, bet_team_a, bet_team_b - 1)
#
#             edge_a_p = edge(matches_all[i].winrate_a, bet_team_a - 1)
#             edge_b_p = edge(1 - matches_all[i].winrate_a, bet_team_b - 1)
#
#             kel_p = kelly(acd_a, edge_a_p, edge_b_p, bet_team_a - 1, bet_team_b - 1)
#             suggestion_a = 0.0
#             suggestion_b = 0.0
#             money_odds_a = 0.0
#             money_odds_b = 0.0
#             if kel_p > 0:
#                 if acd_a == 1:
#                     suggestion_a = kel_p / 16
#                     suggestion_b = 0
#                 if acd_a == 0:
#                     suggestion_a = 0
#                     suggestion_b = kel_p / 16
#             if ans == 1 and acd_a == 1:
#                 total += suggestion_a * money * (matches_all[i].bet_team_a -1)
#                 money_odds_a = suggestion_a * money * (matches_all[i].bet_team_a-1)
#             if ans == 1 and acd_a == 0:
#                 total -= suggestion_b * money
#                 money_odds_b = -suggestion_b * money
#             if ans == 0 and acd_a == 1:
#                 total -= suggestion_a * money
#                 money_odds_a = -suggestion_a * money
#             if ans == 0 and acd_a == 0:
#                 total += suggestion_b * money * (matches_all[i].bet_team_b - 1)
#                 money_odds_b = suggestion_b * money * (matches_all[i].bet_team_b- 1)
#             # print("so tien choi ",total)
#             result.append({
#                 "date": "Today" if check_today(matches_all[i].time) else matches_all[i].time.strftime("%d/%m/%Y"),
#                 "time": matches_all[i].time.strftime("%H:%M"),
#                 "source": matches_all[i].source,
#                 "a": 1,
#                 "team_a": matches_all[i].team_a,
#                 "team_b": matches_all[i].team_b,
#
#                 "vp_odds_team_a": bet_team_a,
#                 "vp_suggestion_team_a": suggestion_a * money,
#                 "vp_odds_team_b": bet_team_b,
#                 "vp_suggestion_team_b": suggestion_b * money,
#
#                 "manual_odds_team_a": str(round(1 / matches_all[i].winrate_a, 2)),
#                 "manual_suggestion_team_a": ans,
#                 "manual_odds_team_b": str(round(1 / (1 - matches_all[i].winrate_a), 2)),
#                 "manual_suggestion_team_b": 1 - ans,
#
#                 "money_team_a": str(round(money_odds_a, 2)),
#                 "revenue_team_a": str(round(total, 2)),
#                 "money_team_b": str(round(money_odds_b, 2)),
#                 "revenue_team_b": str(round(total, 2)),
#             })
#
#     result.reverse()
#     context = {
#         "result": result
#     }
#
#     return render(request, 'bet/vpgame.html', context)


def over(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    t_now = datetime.now()
    end_time = "2019-02-13 11:34:37.710300"
    end_time1 = "2020-03-18"
    time1 = datetime.strptime(end_time1, "%Y-%m-%d")
    matches_all = MatchUpcoming.objects.filter(time__range=(end_time, t_now)).order_by('time')
    result = []
    money = 10000
    pin_money = 0.0
    vp_money = 0.0
    e_money = 0.0
    for item in matches_all:
        if item.match_id and item.winrate_a > 0 and item.winrate_b > 0:
            pin_result_a = 0.0
            pin_result_b = 0.0
            vpgame = BetMatch.objects.filter(match_id=item.match_id)
            egame = BetMatchEGame.objects.filter(match_id=item.match_id)
            match = Match.objects.filter(id=item.match_id)
            ans = -1
            for x in match:
                if x.point_team_a - x.point_team_b > 0:
                    ans = 1
                if x.point_team_b - x.point_team_a > 0:
                    ans = 0
                break
            if item.winrate_a > 0 and item.winrate_a < 1:
                ev_a_p = expectedValue(item.winrate_a, item.bet_team_a-1)
                ev_b_p = expectedValue(1-item.winrate_a, item.bet_team_b-1)

                acd_a_pin = according(ev_a_p, ev_b_p, item.bet_team_a-1, item.bet_team_b-1)

                edge_a_pin = edge(item.winrate_a, item.bet_team_a-1)
                edge_b_pin = edge(1 - item.winrate_a, item.bet_team_b-1)

                kel_pin = kelly(acd_a_pin, edge_a_pin, edge_b_pin, item.bet_team_a-1,  item.bet_team_b-1)

            suggestion_a_pin = 0.0
            suggestion_b_pin = 0.0

            if kel_pin > 0:
                if acd_a_pin == 1:
                    suggestion_a_pin = kel_pin / 16
                    suggestion_b_pin = 0
                if acd_a_pin == 0:
                    suggestion_a_pin = 0
                    suggestion_b_pin = kel_pin / 16

            if ans == 1 and suggestion_a_pin > 0:
                pin_money += suggestion_a_pin * money * (item.bet_team_a - 1)
                pin_result_a = suggestion_a_pin * money * (item.bet_team_a - 1)
            if ans == 1 and suggestion_a_pin == 0:
                pin_money -= suggestion_b_pin * money
                pin_result_b = -suggestion_b_pin * money
            if ans == 0 and suggestion_a_pin > 0:
                pin_money -= suggestion_a_pin * money
                pin_result_a = -suggestion_a_pin * money
            if ans == 0 and suggestion_a_pin == 0:
                pin_money += suggestion_b_pin * money * (item.bet_team_b - 1)
                pin_result_b = suggestion_b_pin * money * (item.bet_team_b - 1)


            vp_odds_team_a = 0.0
            vp_odds_team_b = 0.0
            vp_result_a = 0.0
            vp_result_b = 0.0
            source_vp ="https://www.vpgame.com/prediction/match/csgo/parimutuel"
            # tinh kelly and suggets nha cai vpgame
            w_a_vp = -1
            ans_vp = -1
            for x in vpgame:
                vp_odds_team_a = x.bet_team_a
                vp_odds_team_b = x.bet_team_b
                w_a_vp = x.w_a
                source_vp = x.source
                if x.point_team_a - x.point_team_b > 0:
                    ans_vp = 1
                if x.point_team_b - x.point_team_a > 0:
                    ans_vp = 0
                if x.point_team_b - x.point_team_a == 0:
                    ans_vp = -1
                break
            kel_p = 0.0
            acd_a = -1
            if w_a_vp > 0 and w_a_vp < 1:
                ev_a = expectedValue(w_a_vp, vp_odds_team_a)
                ev_b = expectedValue(1 - w_a_vp, vp_odds_team_b)

                acd_a = according(ev_a, ev_b, vp_odds_team_a, vp_odds_team_b)

                edge_a_p = edge(w_a_vp, vp_odds_team_a)
                edge_b_p = edge(1 - w_a_vp, vp_odds_team_b)

                kel_p = kelly(acd_a, edge_a_p, edge_b_p,  vp_odds_team_a,  vp_odds_team_b)

            suggestion_a = 0.0
            suggestion_b = 0.0

            if kel_p > 0:
                if acd_a == 1:
                    suggestion_a = kel_p / 16
                    suggestion_b = 0
                if acd_a == 0:
                    suggestion_a = 0
                    suggestion_b = kel_p / 16
            if ans_vp == 1 and acd_a == 1:
                vp_money += suggestion_a * money * vp_odds_team_a
                vp_result_a = suggestion_a * money * vp_odds_team_a
            if ans_vp == 1 and acd_a == 0:
                vp_money -= suggestion_b * money
                vp_result_b = -suggestion_b * money
            if ans_vp == 0 and acd_a == 1:
                vp_money -= suggestion_a * money
                vp_result_a = -suggestion_a * money
            if ans_vp == 0 and acd_a == 0:
                vp_money += suggestion_b * money * vp_odds_team_b
                vp_result_b = suggestion_b * money * vp_odds_team_b

            e_odds_team_a = 0.0
            e_odds_team_b = 0.0
            e_result_a = 0.0
            e_result_b = 0.0
            source_e = "https://www.5etop.com/match/index.do"
            # tinh kelly and suggets nha cai 5egane
            w_a_e = -1
            ans_e = -1
            for x in egame:
                e_odds_team_a = x.bet_team_a
                e_odds_team_b = x.bet_team_b
                w_a_e = x.w_a
                source_e = x.source
                if x.point_team_a is None:
                    ans_e = -1
                else:
                    if x.point_team_a - x.point_team_b > 0:
                        ans_e = 1
                    if x.point_team_b - x.point_team_a > 0:
                        ans_e = 0
                    if x.point_team_b - x.point_team_a == 0:
                        ans_e = -1
                break

            acd_e = -1
            kel_e = 0.0
            if w_a_e > 0 and w_a_e < 1:
                ev_a = expectedValue(w_a_e, e_odds_team_a)
                ev_b = expectedValue(1 - w_a_e, e_odds_team_b)

                acd_e = according(ev_a, ev_b, e_odds_team_a, e_odds_team_b)

                edge_a_e = edge(w_a_e, e_odds_team_a)
                edge_b_e = edge(1 - w_a_e, e_odds_team_b)

                kel_e = kelly(acd_e, edge_a_e, edge_b_e, e_odds_team_a, e_odds_team_b)
            suggestion_a_e = 0.0
            suggestion_b_e = 0.0

            if kel_e > 0:
                if acd_e == 1:
                    suggestion_a_e = kel_e / 16
                    suggestion_b_e = 0
                if acd_e == 0:
                    suggestion_a_e = 0
                    suggestion_b_e = kel_e / 16
            if ans_e == 1 and acd_e == 1:
                e_money += suggestion_a_e * money * e_odds_team_a
                e_result_a = suggestion_a_e * money * e_odds_team_a
            if ans_e == 1 and acd_e == 0:
                e_money -= suggestion_b_e * money
                e_result_b = -suggestion_b_e * money
            if ans_e == 0 and acd_e == 1:
                e_money -= suggestion_a_e * money
                e_result_a = -suggestion_a_e * money
            if ans_e == 0 and acd_e == 0:
                e_money += suggestion_b_e * money * e_odds_team_b
                e_result_b = suggestion_b_e * money * e_odds_team_b




            result.append({
                "date": item.time.strftime("%d/%m/%Y"),
                "time": item.time.strftime("%H:%M"),
                "source": item.source,
                "a": 1,
                "team_a": item.team_a,
                "team_b": item.team_b,

                "odds_a": round(1/item.winrate_a, 2),
                "odds_b": round(1/item.winrate_b, 2),

                "result_a": ans,
                "result_b": 1-ans,


                "vp_odds_team_a": round(vp_odds_team_a+1, 2),
                "vp_suggestion_team_a": round(suggestion_a * money, 2),
                "vp_result_a": round(vp_result_a, 2),
                "vp_money_a": round(vp_money, 2),
                "vp_odds_team_b": round(vp_odds_team_b+1, 2),
                "vp_suggestion_team_b": round(suggestion_b * money, 2),
                "vp_result_b": round(vp_result_b, 2),
                "vp_money_b": round(vp_money, 2),
                "source_vp": source_vp,


                "pin_odds_team_a": str(item.bet_team_a),
                "pin_suggestion_team_a": str(round(suggestion_a_pin * money, 2)),
                "pin_result_a": round(pin_result_a, 2),
                "pin_money_a": round(pin_money, 2),
                "pin_odds_team_b": str(item.bet_team_b),
                "pin_suggestion_team_b": str(round(suggestion_b_pin * money, 2)),
                "pin_result_b": round(pin_result_b, 2),
                "pin_money_b": round(pin_money, 2),

                "e_odds_team_a": round(e_odds_team_a + 1, 2),
                "e_suggestion_team_a": round(suggestion_a_e * money, 2),
                "e_result_a": round(e_result_a, 2),
                "e_money_a": round(e_money, 2),
                "e_odds_team_b": round(e_odds_team_b + 1, 2),
                "e_suggestion_team_b": round(suggestion_b_e * money, 2),
                "e_result_b": round(e_result_b, 2),
                "e_money_b": round(e_money, 2),
                "source_e": source_e,
            })

    result.reverse()
    context = {
            "result": result
        }

    return render(request, 'bet/over.html', context)



def egame(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    crawler_over_5etop()
    save_winrate_5e()
    result = []
    match_upcoming1 = BetMatchEGame.objects.all()
    total = 0.0
    money = 10000
    match_upcoming = sorted(match_upcoming1, key=lambda BetMatch: BetMatch.time)
    end_time1 = "2019-11-01"
    time1 = datetime.strptime(end_time1, "%Y-%m-%d")
    for item in match_upcoming:
        if item.time < time1:
            continue
        if item.match_id is None:
            winA = 0
            winB = 0
            if item.w_a > 0 and item.w_a < 1:
                winA = 1 / item.w_a
                winB = 1 / (1 - item.w_a)
            result.append({
                "date": "Today" if check_today(item.time) else item.time.strftime("%d/%m/%Y"),
                "time": item.time.strftime("%H:%M"),
                "source": item.source,
                "a": 1,
                "team_a": item.team_a,
                "team_b": item.team_b,

                "vp_odds_team_a": item.bet_team_a + 1,
                "vp_suggestion_team_a": '-',
                "vp_odds_team_b": item.bet_team_b + 1,
                "vp_suggestion_team_b": '-',

                "manual_odds_team_a": str(round(winA, 2)),
                "manual_suggestion_team_a": '-',
                "manual_odds_team_b": str(round(winB, 2)),
                "manual_suggestion_team_b": '-',

                "money_team_a": '-',
                "revenue_team_a": str(round(total, 2)),
                "money_team_b": '-',
                "revenue_team_b": str(round(total, 2)),
            })
            continue
        if item.point_team_a is None:
            winA = 0
            winB = 0
            if item.w_a > 0 and item.w_a < 1:
                winA = 1 / item.w_a
                winB = 1 / (1 - item.w_a)
            result.append({
                "date": "Today" if check_today(item.time) else item.time.strftime("%d/%m/%Y"),
                "time": item.time.strftime("%H:%M"),
                "source": item.source,
                "a": 1,
                "team_a": item.team_a,
                "team_b": item.team_b,

                "vp_odds_team_a": item.bet_team_a + 1,
                "vp_suggestion_team_a": '-',
                "vp_odds_team_b": item.bet_team_b + 1,
                "vp_suggestion_team_b": '-',

                "manual_odds_team_a": str(round(winA, 2)),
                "manual_suggestion_team_a": '-',
                "manual_odds_team_b": str(round(winB, 2)),
                "manual_suggestion_team_b": '-',

                "money_team_a": '-',
                "revenue_team_a": str(round(total, 2)),
                "money_team_b": '-',
                "revenue_team_b": str(round(total, 2)),
            })
            continue
        if item.point_team_a - item.point_team_b > 0:
            ans = 1
        else:
            ans = 0
        kel_p = -1
        acd_a = -1
        if item.w_a > 0 and item.w_a < 1:
            ev_a = expectedValue(item.w_a, item.bet_team_a)
            ev_b = expectedValue(1 - item.w_a, item.bet_team_b)

            acd_a = according(ev_a, ev_b, item.bet_team_a, item.bet_team_b)

            edge_a_p = edge(item.w_a, item.bet_team_a)
            edge_b_p = edge(1 - item.w_a, item.bet_team_b)

            kel_p = kelly(acd_a, edge_a_p, edge_b_p, item.bet_team_a, item.bet_team_b)
            suggestion_a = 0.0
            suggestion_b = 0.0
            money_odds_a = 0.0
            money_odds_b = 0.0
            if kel_p > 0:
                if acd_a == 1:
                    suggestion_a = kel_p / 16
                    suggestion_b = 0
                if acd_a == 0:
                    suggestion_a = 0
                    suggestion_b = kel_p / 16
            if ans == 1 and acd_a == 1:
                total += suggestion_a * money * item.bet_team_a
                money_odds_a = suggestion_a * money * item.bet_team_a
            if ans == 1 and acd_a == 0:
                total -= suggestion_b * money
                money_odds_b = -suggestion_b * money
            if ans == 0 and acd_a == 1:
                total -= suggestion_a * money
                money_odds_a = -suggestion_a * money
            if ans == 0 and acd_a == 0:
                total += suggestion_b * money * item.bet_team_b
                money_odds_b = suggestion_b * money * item.bet_team_b
            result.append({
                "date": "Today" if check_today(item.time) else item.time.strftime("%d/%m/%Y"),
                "time": item.time.strftime("%H:%M"),
                "source": item.source,
                "a": 1,
                "team_a": item.team_a,
                "team_b": item.team_b,

                "vp_odds_team_a": item.bet_team_a+1,
                "vp_suggestion_team_a": suggestion_a * money,
                "vp_odds_team_b": item.bet_team_b+1,
                "vp_suggestion_team_b": suggestion_b * money,


                "manual_odds_team_a": str(round(1 / item.w_a, 2)),
                "manual_suggestion_team_a": ans,
                "manual_odds_team_b": str(round(1 / (1 - item.w_a), 2)),
                "manual_suggestion_team_b": 1-ans,

                "money_team_a": str(round(money_odds_a, 2)),
                "revenue_team_a": str(round(total, 2)),
                "money_team_b": str(round(money_odds_b, 2)),
                "revenue_team_b": str(round(total, 2)),
            })

    result.reverse()
    context = {
        "result": result
    }

    return render(request, 'bet/vpgame.html', context)

def crawlvp(request):
    call_command('crawler_2_bet')
    return HttpResponseRedirect('/vpgame')


def crawl_up(request):
    link="https://m.vpgame.com/prediction/api/prediction/matches?category=csgo&offset=0&limit=20&status=normal&order=asc"
    upcomming_vp(link)
    upcomming_5etop()
    map_up_5e()
    map_up_vp()
    return HttpResponseRedirect('/bet')

def vpgameDown(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    save_winrate_vp()
    result = []
    match_upcoming1 = BetMatch.objects.all()
    total = 0.0
    money = 10000
    match_upcoming = sorted(match_upcoming1, key=lambda BetMatch: BetMatch.time)
    end_time1 = "2019-11-01"
    time1 = datetime.strptime(end_time1, "%Y-%m-%d")
    for item in match_upcoming:
        if item.time < time1:
            continue
        if item.match_id is None:
            winA= 0
            winB=0
            if item.w_a > 0 and item.w_a < 1:
                winA= 1/item.w_a
                winB= 1/(1-item.w_a)
            # result.append({
            #     "date": "Today" if check_today(item.time) else item.time.strftime("%d/%m/%Y"),
            #     "time": item.time.strftime("%H:%M"),
            #     "source": item.source,
            #     "a": 1,
            #     "team_a": item.team_a,
            #     "team_b": item.team_b,
            #
            #     "vp_odds_team_a": item.bet_team_a + 1,
            #     "vp_suggestion_team_a": '-',
            #     "vp_odds_team_b": item.bet_team_b + 1,
            #     "vp_suggestion_team_b": '-',
            #
            #     "manual_odds_team_a": str(round(winA, 2)),
            #     "manual_suggestion_team_a": '-',
            #     "manual_odds_team_b": str(round(winB, 2)),
            #     "manual_suggestion_team_b": '-',
            #
            #     "money_team_a": '-',
            #     "revenue_team_a": str(round(total, 2)),
            #     "money_team_b": '-',
            #     "revenue_team_b": str(round(total, 2)),
            # })
            continue
        if item.point_team_a - item.point_team_b > 0:
            ans = 1
        if item.point_team_b - item.point_team_a > 0:
            ans = 0
        if item.point_team_b - item.point_team_a == 0:
            ans = -1
        kel_p = -1
        acd_a = -1
        if item.w_a > 0 and item.w_a < 1:
            ev_a = expectedValue(item.w_a, item.bet_team_a)
            ev_b = expectedValue(1 - item.w_a, item.bet_team_b)

            acd_a = according(ev_a, ev_b, item.bet_team_a, item.bet_team_b)

            edge_a_p = edge(item.w_a, item.bet_team_a)
            edge_b_p = edge(1 - item.w_a, item.bet_team_b)

            kel_p = kelly(acd_a, edge_a_p, edge_b_p, item.bet_team_a, item.bet_team_b)
            suggestion_a = 0.0
            suggestion_b = 0.0
            money_odds_a = 0.0
            money_odds_b = 0.0
            if kel_p > 0:
                if acd_a == 1:
                    suggestion_a = kel_p / 16
                    suggestion_b = 0
                if acd_a == 0:
                    suggestion_a = 0
                    suggestion_b = kel_p / 16
            if suggestion_a > 0 and item.bet_team_a < 1:
                continue
            if suggestion_b > 0 and item.bet_team_b < 1:
                continue
            if ans == 1 and acd_a == 1:
                total += suggestion_a * money * item.bet_team_a
                money_odds_a = suggestion_a * money * item.bet_team_a
            if ans == 1 and acd_a == 0:
                total -= suggestion_b * money
                money_odds_b = -suggestion_b * money
            if ans == 0 and acd_a == 1:
                total -= suggestion_a * money
                money_odds_a = -suggestion_a * money
            if ans == 0 and acd_a == 0:
                total += suggestion_b * money * item.bet_team_b
                money_odds_b = suggestion_b * money * item.bet_team_b
            result.append({
                "date": "Today" if check_today(item.time) else item.time.strftime("%d/%m/%Y"),
                "time": item.time.strftime("%H:%M"),
                "source": item.source,
                "a": 1,
                "team_a": item.team_a,
                "team_b": item.team_b,

                "vp_odds_team_a": item.bet_team_a+1,
                "vp_suggestion_team_a": suggestion_a * money,
                "vp_odds_team_b": item.bet_team_b+1,
                "vp_suggestion_team_b": suggestion_b * money,


                "manual_odds_team_a": str(round(1 / item.w_a, 2)),
                "manual_suggestion_team_a": ans,
                "manual_odds_team_b": str(round(1 / (1 - item.w_a), 2)),
                "manual_suggestion_team_b": 1-ans,

                "money_team_a": str(round(money_odds_a, 2)),
                "revenue_team_a": str(round(total, 2)),
                "money_team_b": str(round(money_odds_b, 2)),
                "revenue_team_b": str(round(total, 2)),
            })

    result.reverse()
    context = {
        "result": result
    }

    return render(request, 'bet/vpgame.html', context)