# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import BetUpcoming, MatchUpcoming
from datetime import timedelta, datetime
from .constant import day, pinnacle, five_etop, vp_game
from django.core.management import call_command


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/bet/')
    return HttpResponseRedirect('/login/')


def check_today(time):
    t_now = datetime.now()
    return t_now.day == time.day and t_now.month == time.month and t_now.year == time.year


def refresh(request):
    call_command('crawler_10_match_upcoming')
    # import time
    # time.sleep(20)
    return HttpResponse(1, content_type='application/json')


def detail(request):
    # set limit time for query: in 2 next day
    t_now = datetime.now()
    time_limit = datetime.now().replace(hour=23, minute=59, second=59) + timedelta(days=day)

    # get matches in 2 next day, oder_by time
    matches = MatchUpcoming.objects.filter(time__range=(t_now, time_limit)).order_by('time')
    result = []
    for item in matches:
        # get odds of banker
        bets = BetUpcoming.objects.filter(match_id=item.id)
        if bets.count() == 0:
            # if match have no bet -> continue
            # else append bet to result
            continue

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

            "pin_odds_team_a": pin_odds_team_a,
            "pin_suggestion_team_a": "-",
            "pin_odds_team_b": pin_odds_team_b,
            "pin_suggestion_team_b": "-",

            "manual_odds_team_a": "-",
            "manual_suggestion_team_a": "-",
            "manual_odds_team_b": "-",
            "manual_suggestion_team_b": "-",
        })

    context = {
        "result": result
    }

    return render(request, 'bet/index.html', context)
