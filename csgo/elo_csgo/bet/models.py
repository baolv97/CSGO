# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils import timezone

ELO = 1800


class Match(models.Model):
    time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian thi đấu")
    type = models.CharField(max_length=10, null=True, blank=True, verbose_name="Thể thức chơi")
    team_a = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội A")
    id_team_a = models.IntegerField(null=True, blank=True, verbose_name="ID đội A")
    point_team_a = models.IntegerField(null=True, blank=True, verbose_name="Điểm đội A")
    team_b = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội B")
    id_team_b = models.IntegerField(null=True, blank=True, verbose_name="ID đội B")
    point_team_b = models.IntegerField(null=True, blank=True, verbose_name="Điểm đội B")
    source = models.CharField(max_length=500, null=True, blank=True, verbose_name="Nguồn")
    bet_team_a = models.FloatField(null=True, blank=True)
    bet_team_b = models.FloatField(null=True, blank=True)
    source_bet = models.CharField(max_length=500, null=True, blank=True, verbose_name="Nguồn bet")
    w_a = models.FloatField(null=True, blank=True, verbose_name="Tỷ lệ thắng đội A", default=0)

    def __str__(self):
        result = "{} ({}:{}) {}".format(self.team_a, self.point_team_a, self.point_team_b, self.team_b)
        return result

    class Meta:
        db_table = "d_cs_go_match"
        verbose_name = "Trận đấu"
        verbose_name_plural = "Trận đấu"
        indexes = [
            models.Index(fields=['source', ]),
            models.Index(fields=['time', ]),
            models.Index(fields=['team_a', ]),
            models.Index(fields=['point_team_a', ]),
            models.Index(fields=['team_b', ]),
            models.Index(fields=['point_team_b', ]),
        ]


class BetMatch(models.Model):
    time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian thi đấu")
    team_a = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội A")
    id_team_a = models.IntegerField(null=True, blank=True, verbose_name="ID đội A")
    point_team_a = models.IntegerField(null=True, blank=True, verbose_name="Điểm đội A")
    team_b = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội B")
    id_team_b = models.IntegerField(null=True, blank=True, verbose_name="ID đội B")
    point_team_b = models.IntegerField(null=True, blank=True, verbose_name="Điểm đội B")
    bet_team_a = models.FloatField(null=True, blank=True)
    bet_team_b = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=500, null=True, blank=True, verbose_name="Nguồn")
    w_a = models.FloatField(null=True, blank=True, verbose_name="Tỷ lệ thắng đội A", default=0)
    match_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "d_cs_go_bet_match"
        verbose_name = "BET"
        verbose_name_plural = "BET"
        indexes = [
            models.Index(fields=['time', ]),
            models.Index(fields=['team_a', ]),
            models.Index(fields=['point_team_a', ]),
            models.Index(fields=['team_b', ]),
            models.Index(fields=['point_team_b', ]),
        ]


class BetMatchEGame(models.Model):
    time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian thi đấu")
    team_a = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội A")
    id_team_a = models.IntegerField(null=True, blank=True, verbose_name="ID đội A")
    point_team_a = models.IntegerField(null=True, blank=True, verbose_name="Điểm đội A")
    team_b = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội B")
    id_team_b = models.IntegerField(null=True, blank=True, verbose_name="ID đội B")
    point_team_b = models.IntegerField(null=True, blank=True, verbose_name="Điểm đội B")
    bet_team_a = models.FloatField(null=True, blank=True)
    bet_team_b = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=500, null=True, blank=True, verbose_name="Nguồn")
    w_a = models.FloatField(null=True, blank=True, verbose_name="Tỷ lệ thắng đội A", default=0)
    match_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "d_cs_go_bet_match_egame"
        verbose_name = "BET"
        verbose_name_plural = "BET"
        indexes = [
            models.Index(fields=['time', ]),
            models.Index(fields=['team_a', ]),
            models.Index(fields=['point_team_a', ]),
            models.Index(fields=['team_b', ]),
            models.Index(fields=['point_team_b', ]),
        ]


class BanPick(models.Model):
    match = models.ForeignKey(
        Match,
        null=True, blank=True,
        on_delete=models.CASCADE,
        verbose_name="Trận đấu"
    )
    order = models.IntegerField(null=True, blank=True, verbose_name="STT")
    team = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội")
    ban = models.CharField(max_length=50, null=True, blank=True)
    pick = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "d_cs_go_ban_pick"
        verbose_name = "Ban - Pick"
        verbose_name_plural = "Ban - Pick"


class Result(models.Model):
    match = models.ForeignKey(
        Match,
        null=True, blank=True,
        on_delete=models.CASCADE,
        verbose_name="Trận đấu"
    )
    map = models.CharField(max_length=50, null=True, blank=True, verbose_name="Bản đồ")
    half = models.IntegerField(null=True, blank=True, verbose_name="Hiệp")
    team = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội")
    point = models.IntegerField(null=True, blank=True, verbose_name="Điểm")

    class Meta:
        db_table = "d_cs_go_result"
        verbose_name = "Kết quả từng hiệp"
        verbose_name_plural = "Kết quả từng hiệp"


class Performance(models.Model):
    match = models.ForeignKey(
        Match,
        null=True, blank=True,
        on_delete=models.CASCADE,
        verbose_name="Trận đấu"
    )
    map = models.CharField(max_length=50, null=True, blank=True, verbose_name="Bản đồ")
    team = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội")
    player = models.CharField(max_length=50, null=True, blank=True, verbose_name="Người chơi")
    id_player = models.IntegerField(null=True, blank=True, verbose_name="ID Người chơi")
    kill = models.IntegerField(null=True, blank=True)
    death = models.IntegerField(null=True, blank=True)
    adr = models.FloatField(null=True, blank=True)
    kast = models.FloatField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    result = models.IntegerField(null=True, blank=True)
    bet = models.FloatField(null=True, blank=True, default=0)
    elo = models.FloatField(null=True, blank=True, default=ELO)
    check = models.FloatField(null=True, blank=True, default=0)
    time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian thi đấu")

    def __str__(self):
        return self.player if self.player else "-"

    class Meta:
        db_table = "d_cs_go_performance"
        verbose_name = "Hiệu suất"
        verbose_name_plural = "Hiệu suất"


class Player(models.Model):
    team = models.CharField(max_length=200, null=True, blank=True, verbose_name="Đội")
    id_player = models.IntegerField(null=True, blank=True, verbose_name="ID Người chơi")
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Người chơi")
    elo = models.FloatField(null=True, blank=True, default=ELO)

    def __str__(self):
        if self.team and self.id_player and self.name:
            return "({}) - {} - {}".format(self.team, self.id_player, self.name)
        return "-"

    class Meta:
        db_table = "d_cs_go_player"


# trận đấu sắp diễn ra
class MatchUpcoming(models.Model):
    time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian thi đấu")
    type = models.CharField(max_length=10, null=True, blank=True, verbose_name="Thể thức chơi")
    team_a = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội A")
    id_team_a = models.IntegerField(null=True, blank=True, verbose_name="ID đội A")
    team_b = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đội B")
    id_team_b = models.IntegerField(null=True, blank=True, verbose_name="ID đội B")
    source = models.CharField(max_length=500, null=True, blank=True, verbose_name="Nguồn")
    created_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
    bet_team_a = models.FloatField(null=True, blank=True, default=0.0)
    bet_team_b = models.FloatField(null=True, blank=True, default=0.0)
    suggestion_a = models.FloatField(null=True, blank=True, default=0.0)
    suggestion_b = models.FloatField(null=True, blank=True, default=0.0)
    bet_team_a_e = models.FloatField(null=True, blank=True, default=0.0)
    bet_team_b_e = models.FloatField(null=True, blank=True, default=0.0)
    suggestion_a_e = models.FloatField(null=True, blank=True, default=0.0)
    suggestion_b_e = models.FloatField(null=True, blank=True, default=0.0)
    winrate_a = models.FloatField(null=True, blank=True, default=0.0)
    winrate_b = models.FloatField(null=True, blank=True, default=0.0)
    match_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        result = "{} ({}) {}".format(self.team_a, self.time, self.team_b)
        return result

    class Meta:
        db_table = "d_cs_go_match_upcoming"
        verbose_name = "Trận đấu sắp diễn ra"
        verbose_name_plural = "Trận đấu sắp diễn ra"
        indexes = [
            models.Index(fields=['source', ]),
            models.Index(fields=['time', ]),
            models.Index(fields=['team_a', ]),
            models.Index(fields=['team_b', ]),
        ]


class MatchUpcomingPlayer(models.Model):
    match_upcoming = models.ForeignKey(
        MatchUpcoming,
        null=True, blank=True,
        on_delete=models.CASCADE,
        verbose_name="Trận đấu"
    )
    team = models.CharField(max_length=200, null=True, blank=True, verbose_name="Đội")
    id_player = models.IntegerField(null=True, blank=True, verbose_name="ID Người chơi")
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name="Người chơi")

    class Meta:
        db_table = "d_cs_go_match_upcoming_player"


# tỷ lệ BET của các nhà cái với những trận upcoming
class BetUpcoming(models.Model):
    match = models.ForeignKey(
        MatchUpcoming,
        null=True, blank=True,
        on_delete=models.CASCADE,
        verbose_name="Trận đấu"
    )
    banker = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nhà cái")
    bet_team_a = models.FloatField(null=True, blank=True)
    bet_team_b = models.FloatField(null=True, blank=True)

    def __str__(self):
        result = "{}: {} ({} - {}) {}".format(self.banker, self.match.team_a, self.bet_team_a, self.bet_team_b,
                                              self.match.team_b)
        return result

    class Meta:
        db_table = "d_cs_go_bet_upcoming"
        verbose_name = "BET - Trận đấu sắp diễn ra"
        verbose_name_plural = "BET - Trận đấu sắp diễn ra"


class BankRoll(models.Model):
    total = models.IntegerField(verbose_name="Tổng tiền")
    change = models.IntegerField(null=True, blank=True, verbose_name="Thay đổi")
    time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian")

    def __str__(self):
        return self.total

    class Meta:
        db_table = "d_cs_go_bank_roll"
        verbose_name = "Tổng tiền"
        verbose_name_plural = "Tổng tiền"
