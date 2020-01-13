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
    call_command('crawler_9_train_elo_for_player')
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
        elo_a = -1.0
        elo_b = -1.0
        count = 0
        for i in e:
            if i.team == item.team_a:
                elo_a += i.elo
                count += 1
        if count >= 5:
            elo_a = elo_a / count
        else:
            elo_a = -1
        count = 0
        for i in e:
            if i.team == item.team_b:
                count += 1
                elo_b += i.elo
        if count >= 5:
            elo_b = elo_b / count
        else:
            elo_b = -1
        if elo_a > 0 and elo_b > 0:
            w_a = winRate(elo_a, elo_b)
            w_b = 1 - w_a
        else:
            w_a = -1
            w_b = -1

        pin_odds_team_a = "-"
        pin_odds_team_b = "-"
        vp_odds_team_a = "-"
        vp_odds_team_b = "-"
        etop_odds_team_a = "-"
        etop_odds_team_b = "-"
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

        ev_a = expectedValue(w_a, bet.bet_team_a - 1)
        ev_b = expectedValue(w_a, bet.bet_team_b - 1)

        acd_a = according(ev_a, ev_b)

        edge_a = edge(w_a, bet.bet_team_a - 1)
        edge_b = edge(w_b, bet.bet_team_b - 1)

        kel = kelly(acd_a, edge_a, edge_b, bet.bet_team_a - 1, bet.bet_team_b - 1)

        kelly_a = 0
        kelly_b = 0

        if kel > 0:
            if acd_a == 1:
                kelly_a = kel / 8
                kelly_b = 0
            if acd_a == 0:
                kelly_a = 0
                kelly_b = kel / 8

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

            "5e_odds_team_a": etop_odds_team_a,
            "5e_suggestion_team_a": "-",
            "5e_odds_team_b": etop_odds_team_b,
            "5e_suggestion_team_b": "-",

            "pin_odds_team_a": str(pin_odds_team_a),
            "pin_suggestion_team_a": str(round(kelly_a, 3)),
            "pin_odds_team_b": str(pin_odds_team_b),
            "pin_suggestion_team_b": str(round(kelly_b, 3)),

            "manual_odds_team_a": str(round(w_a, 2)),
            "manual_suggestion_team_a": "-",
            "manual_odds_team_b": str(round(w_b, 2)),
            "manual_suggestion_team_b": "-",
        })

    context = {
        "result": result
    }

    return render(request, 'bet/index.html', context)
