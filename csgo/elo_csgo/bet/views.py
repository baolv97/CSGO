# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import BetUpcoming, MatchUpcoming
from datetime import timedelta, datetime
from .constant import day, pinnacle, five_etop, vp_game
from django.core.management import call_command
from .models import *


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


def winRate(elo_a, elo_b):
    q_a = pow(10, elo_a / 400)
    q_b = pow(10, elo_b / 400)

    return q_a / (q_a + q_b)


def expectedValue(w_a, bet_a):
    return w_a * bet_a - (1 - w_a) * 1


def according(expected_value_a, expected_value_b):
    if expected_value_a < 0 and expected_value_b < 0:
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


def detail(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login/')
    # set limit time for query: in 2 next day
    t_now = datetime.now()
    time_limit = datetime.now().replace(hour=23, minute=59, second=59) + timedelta(days=day)
    print(time_limit)
    # get matches in 2 next day, oder_by time
    matches = MatchUpcoming.objects.filter(time__range=(t_now, time_limit)).order_by('time')
    result = []
    e = Player.objects.all()
    for item in matches:
        # get odds of banker
        bets = BetUpcoming.objects.filter(match_id=item.id)
        if bets.count() == 0:
            # if match have no bet -> continue
            # else append bet to result
            continue
        # get total elo team_a and team_b
        total_elo_a = 0
        total_elo_b = 0
        players = MatchUpcomingPlayer.objects.filter(match_upcoming=item)
        for p in players:
            player = Player.objects.filter(name=p.name)
            if player.count() > 1:
                player = player.filter(id_player=p.id_player)
            player = player.first()
            player_elo = player.elo if player else 1800

            if p.team == item.team_a:
                total_elo_a += player_elo
                #print(p.team, player_elo)
            else:
                total_elo_b += player_elo
                #print(p.team, player_elo)
        print("total_elo team A", total_elo_a)
        print("total_elo team B", total_elo_b)
        elo_a = total_elo_a / 5
        elo_b = total_elo_b / 5
        w_a = winRate(elo_a, elo_b)
        w_b = 1 - w_a
        print("win rate team A", w_a)
        print("win rate team B", w_b)
        #set up suggestion nha cai pin
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

        acd_a = according(ev_a_pin, ev_b_pin)

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
        # set up suggestion nha cai 5etop
        ev_a_e = expectedValue(w_a, etop_odds_team_a)
        ev_b_e = expectedValue(w_b, etop_odds_team_b)

        acd_a_e = according(ev_a_e, ev_b_e)

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
        print("5e kel ", kel_e/8)

        if kel_e > 0:
            if acd_a == 1:
                kelly_a_e = kel_e / 8
                kelly_b_e = 0
            if acd_a == 0:
                kelly_a_e = 0
                kelly_b_e = kel_e / 8

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

            "5e_odds_team_a": str(etop_odds_team_a),
            "5e_suggestion_team_a": str(round(kelly_a_e, 3)),
            "5e_odds_team_b": str(etop_odds_team_b),
            "5e_suggestion_team_b": str(round(kelly_b_e, 3)),

            "pin_odds_team_a": str(pin_odds_team_a),
            "pin_suggestion_team_a": str(round(kelly_a_p, 3)),
            "pin_odds_team_b": str(pin_odds_team_b),
            "pin_suggestion_team_b": str(round(kelly_b_p, 3)),

            "manual_odds_team_a": str(round(1 / w_a, 2)),
            "manual_suggestion_team_a": "-",
            "manual_odds_team_b": str(round(1 / w_b, 2)),
            "manual_suggestion_team_b": "-",
        })

    context = {
        "result": result
    }

    return render(request, 'bet/index.html', context)
