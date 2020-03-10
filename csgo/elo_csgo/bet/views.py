# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import BetUpcoming, MatchUpcoming
from datetime import timedelta, datetime
from .constant import day, pinnacle, five_etop, vp_game
from django.core.management import call_command
from .models import *
import threading
import time


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/bet/')
    return HttpResponseRedirect('/login/')


def check_today(time):
    t_now = datetime.now()
    return t_now.day == time.day and t_now.month == time.month and t_now.year == time.year


def refresh(request):
    # call_command('crawler_9_train_elo_for_player')
    call_command('crawler_10_match_upcoming')
    # import time
    # time.sleep(20)
    return HttpResponse(1, content_type='application/json')


def training_elo(request):
    try:
        t1 = threading.Thread(target=call_command, args=('crawler_9_train_elo_for_player',))
        t1.start()
    except:
        print("err")

    # call_command('crawler_9_train_elo_for_player')
    return HttpResponse(1, content_type='application/json')


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
                print(p.team, p.name, player_elo)
                d_team_a += 1
            else:
                total_elo_b += player_elo
                print(p.team, p.name, player_elo)
                d_team_b += 1
        print("total_elo team A", total_elo_a)
        print("total_elo team B", total_elo_b)
        print("nguoi A", d_team_a)
        print("nguoi B", d_team_b)
        if d_team_a != 0 and d_team_b !=0:
            elo_a = total_elo_a / d_team_a
            elo_b = total_elo_b / d_team_b
        else:
            elo_a = 0
            elo_b = 0
        w_a = winRate(elo_a, elo_b)
        w_b = 1 - w_a
        print("win rate team A", w_a)
        print("win rate team B", w_b)
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
        print("pin ", pin_odds_team_a)
        print("pin ", pin_odds_team_b)
        print("5e", etop_odds_team_a)
        print("5e", etop_odds_team_b)
        # set up suggestion nha cai pin
        ev_a_pin = expectedValue(w_a, pin_odds_team_a - 1)
        ev_b_pin = expectedValue(w_b, pin_odds_team_b - 1)

        acd_a = according(ev_a_pin, ev_b_pin, pin_odds_team_a - 1,  pin_odds_team_b - 1)

        edge_a_p = edge(w_a, pin_odds_team_a - 1)
        edge_b_p = edge(w_b, pin_odds_team_b - 1)

        kel_p = kelly(acd_a, edge_a_p, edge_b_p, pin_odds_team_a - 1, pin_odds_team_b - 1)
        print("pin ev ", ev_a_pin)
        print("pin ev ", ev_b_pin)
        print("pin acd ", acd_a)
        print("pin edg ", edge_a_p)
        print("pin edg ", edge_b_p)
        print("pin kel ", kel_p / 8)
        kelly_a_p = 0
        kelly_b_p = 0

        if kel_p > 0:
            if acd_a == 1:
                kelly_a_p = kel_p / 8
                kelly_b_p = 0
            if acd_a == 0:
                kelly_a_p = 0
                kelly_b_p = kel_p / 8
        matches_all[item.id - 109].bet_team_a = pin_odds_team_a
        matches_all[item.id - 109].bet_team_b = pin_odds_team_b
        matches_all[item.id - 109].suggestion_a = kelly_a_p
        matches_all[item.id - 109].suggestion_b = kelly_b_p
        print("baobao", matches_all[item.id - 109].bet_team_a, pin_odds_team_a)
        # set up suggestion nha cai 5etop
        ev_a_e = expectedValue(w_a, etop_odds_team_a)
        ev_b_e = expectedValue(w_b, etop_odds_team_b)

        acd_a_e = according(ev_a_e, ev_b_e, etop_odds_team_a, etop_odds_team_b)

        edge_a_e = edge(w_a, etop_odds_team_a)
        edge_b_e = edge(w_b, etop_odds_team_b)

        kel_e = kelly(acd_a_e, edge_a_e, edge_b_e, etop_odds_team_a, etop_odds_team_b)

        kelly_a_e = 0
        kelly_b_e = 0
        print("5e ev ", ev_a_e)
        print("5e ev ", ev_b_e)
        print("5e acd ", acd_a_e)
        print("5e edg ", edge_a_e)
        print("5e edg ", edge_b_e)
        print("5e kel ", kel_e / 8)

        if kel_e > 0:
            if acd_a == 1:
                kelly_a_e = kel_e / 8
                kelly_b_e = 0
            if acd_a == 0:
                kelly_a_e = 0
                kelly_b_e = kel_e / 8
        matches_all[item.id - 109].bet_team_a_e = etop_odds_team_a
        matches_all[item.id - 109].bet_team_b_e = etop_odds_team_b
        matches_all[item.id - 109].suggestion_a_e = kelly_a_e
        matches_all[item.id - 109].suggestion_b_e = kelly_b_e
        matches_all[item.id - 109].winrate_a = w_a
        matches_all[item.id - 109].winrate_b = w_b
        matches_all[item.id - 109].save()
        result.append({
            "date": "Today" if check_today(item.time) else item.time.strftime("%d/%m/%Y"),
            "time": item.time.strftime("%H:%M"),
            "source": item.source,
            "a": 1,
            "team_a": item.team_a,
            "team_b": item.team_b,

            "vp_odds_team_a": vp_odds_team_a,
            "vp_suggestion_team_a": "-",
            "vp_odds_team_b": vp_odds_team_b,
            "vp_suggestion_team_b": "-",

            "5e_odds_team_a": str(etop_odds_team_a+1),
            "5e_suggestion_team_a": str(round(kelly_a_e, 6)),
            "5e_odds_team_b": str(etop_odds_team_b+1),
            "5e_suggestion_team_b": str(round(kelly_b_e, 6)),

            "pin_odds_team_a": str(pin_odds_team_a),
            "pin_suggestion_team_a": str(round(kelly_a_p, 6)),
            "pin_odds_team_b": str(pin_odds_team_b),
            "pin_suggestion_team_b": str(round(kelly_b_p, 6)),

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
    end_time = "2019-02-13 11:34:37.710300"
    matches_all = MatchUpcoming.objects.filter(time__range=(end_time, t_now)).order_by('time')
    result = []
    total_money = 10000.0
    for i in range(len(matches_all)):
        if matches_all[i].winrate_a == 0:
            continue
        check = 0
        for j in range(i):
            if matches_all[i].time == matches_all[j].time and matches_all[i].team_a == matches_all[j].team_a and matches_all[i].team_b == matches_all[j].team_b:
                check = 1
                break
        if check == 1:
            # print("baobao")
            continue

        t_now = matches_all[i].time.strftime("%Y-%m-%d")+" 00:00:00"
        #print(t_now)
        time = datetime.strptime(t_now, '%Y-%m-%d %H:%M:%S')
        time_limit = time.replace(hour=23, minute=59, second=59) + 1/2*timedelta(days=day)
        # print(time_limit)
        match = Match.objects.filter(time__range=(t_now, time_limit)).order_by('time')
        point_team_a = -1
        point_team_b = -1
        money_odds_a = 0.0
        money_odds_b = 0.0
        for x in match:
            if x.team_a == matches_all[i].team_a and x.team_b == matches_all[i].team_b:
                if x.point_team_a-x.point_team_b > 0:
                    point_team_a = 1
                    point_team_b = 0
                if x.point_team_a - x.point_team_b < 0:
                    point_team_a = 0
                    point_team_b = 1
                if x.id == 9396 or x.id == 9408:
                    point_team_a = -1
                    point_team_b = -1
                break
        # if point_team_a == 1 and matches_all[i].bet_team_a > 1/matches_all[i].winrate_a and matches_all[i].bet_team_a < matches_all[i].bet_team_b:
        #     print("win", matches_all[i].bet_team_a, 1/matches_all[i].winrate_a)
        # if point_team_a == 0 and matches_all[i].bet_team_a > 1 / matches_all[i].winrate_a and matches_all[i].bet_team_a < matches_all[i].bet_team_b:
        #     print("lose", matches_all[i].bet_team_a, 1/matches_all[i].winrate_a)
        # if point_team_b == 1 and matches_all[i].bet_team_b > 1/matches_all[i].winrate_b and matches_all[i].bet_team_a > matches_all[i].bet_team_b:
        #     print("win", matches_all[i].bet_team_b, 1/matches_all[i].winrate_b)
        # if point_team_b == 0 and matches_all[i].bet_team_b > 1/matches_all[i].winrate_b and matches_all[i].bet_team_a > matches_all[i].bet_team_b:
        #     print("lose", matches_all[i].bet_team_b, 1/matches_all[i].winrate_b)
        if matches_all[i].team_a == "HAVU" or matches_all[i].team_b == "HAVU":
            print(matches_all[i].suggestion_a,  point_team_a)
        if matches_all[i].suggestion_a > 0.005 and matches_all[i].suggestion_a < 0.035:
            if point_team_a == 1:
                money_odds_a = total_money * matches_all[i].suggestion_a * (matches_all[i].bet_team_a - 1)
                total_money = total_money + money_odds_a
            if point_team_a == 0:
                money_odds_a = -total_money * matches_all[i].suggestion_a
                total_money = total_money + money_odds_a

        if matches_all[i].suggestion_b > 0.005 and matches_all[i].suggestion_b < 0.035:
            if point_team_b == 1:
                money_odds_b = total_money * matches_all[i].suggestion_b * (matches_all[i].bet_team_b - 1)
                total_money = total_money + money_odds_b
            if point_team_b == 0:
                money_odds_b = -total_money * matches_all[i].suggestion_b
                total_money = total_money + money_odds_b


        winrate_a = 0.0
        winrate_b = 0.0
        if matches_all[i].winrate_a != 0 and matches_all[i].winrate_b != 0:
            winrate_a = 1 / matches_all[i].winrate_a
            winrate_b = 1 / matches_all[i].winrate_b
        result.append({
            "date": matches_all[i].time.strftime("%d/%m/%Y"),
            "time": matches_all[i].time.strftime("%H:%M"),
            "source": matches_all[i].source,
            "a": 1,
            "team_a": matches_all[i].team_a,
            "team_b": matches_all[i].team_b,

            "vp_odds_team_a": 0.0,
            "vp_suggestion_team_a": "-",
            "vp_odds_team_b": 0.0,
            "vp_suggestion_team_b": "-",

            "5e_odds_team_a": str(matches_all[i].bet_team_a_e),
            "5e_suggestion_team_a": str(round(matches_all[i].suggestion_a_e, 6)),
            "5e_odds_team_b": str(matches_all[i].bet_team_b_e),
            "5e_suggestion_team_b": str(round(matches_all[i].suggestion_b_e, 6)),

            "pin_odds_team_a": str(matches_all[i].bet_team_a),
            "pin_suggestion_team_a": str(round(matches_all[i].suggestion_a, 6)),
            "pin_odds_team_b": str(matches_all[i].bet_team_b),
            "pin_suggestion_team_b": str(round(matches_all[i].suggestion_b, 6)),

            "manual_odds_team_a": str(round(winrate_a, 2)),
            "manual_suggestion_team_a": point_team_a,
            "manual_odds_team_b": str(round(winrate_b, 2)),
            "manual_suggestion_team_b": point_team_b,

            "money_team_a": str(round(money_odds_a, 2)),
            "revenue_team_a": str(round(total_money, 2)),
            "money_team_b": str(round(money_odds_b, 2)),
            "revenue_team_b": str(round(total_money, 2)),
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
