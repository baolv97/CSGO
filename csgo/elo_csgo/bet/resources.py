from import_export import resources, fields
from .models import *


class MatchResource(resources.ModelResource):
    class Meta:
        model = Match


class BetMatchResource(resources.ModelResource):
    class Meta:
        model = BetMatch


class BanPickResource(resources.ModelResource):
    class Meta:
        model = BanPick


class ResultResource(resources.ModelResource):
    class Meta:
        model = Result


class PerformanceResource(resources.ModelResource):
    class Meta:
        model = Performance
