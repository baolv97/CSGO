# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from import_export.admin import ImportExportMixin
from .resources import *


class MatchAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = MatchResource

    # list_display = ['bet_team_a', 'bet_team_b']

    def has_export_permission(self, request):
        return True

    def has_import_permission(self, request):
        return False

    # def get_queryset(self, request):
    #     return Match.objects.exclude(bet_team_a=None, bet_team_b=None).order_by('-id')


class BetMatchAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = BetMatchResource

    def has_export_permission(self, request):
        return True

    def has_import_permission(self, request):
        return False


class BanPickAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = BanPickResource
    list_display = ['match']

    def has_export_permission(self, request):
        return True

    def has_import_permission(self, request):
        return False

    # def get_queryset(self, request):
    #     return BanPick.objects.exclude(match__bet_team_a=None, match__bet_team_b=None).order_by('-id')


class ResultAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = ResultResource

    def has_export_permission(self, request):
        return True

    def has_import_permission(self, request):
        return False

    # def get_queryset(self, request):
    #     return Result.objects.exclude(match__bet_team_a=None, match__bet_team_b=None).order_by('-id')


class PerformanceAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = PerformanceResource

    def has_export_permission(self, request):
        return True

    def has_import_permission(self, request):
        return False

    # def get_queryset(self, request):
    #     return Performance.objects.exclude(match__bet_team_a=None, match__bet_team_b=None).order_by('-id')


admin.site.register(Match, MatchAdmin)
admin.site.register(BetMatch, BetMatchAdmin)
admin.site.register(BanPick, BanPickAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Performance, PerformanceAdmin)
