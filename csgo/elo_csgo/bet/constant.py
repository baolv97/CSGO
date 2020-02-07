import datetime as my_datetime_1

# HLTV
max_offset = 8709
time_now = my_datetime_1.datetime.now().strftime("%Y-%m-%d")
last_year = (my_datetime_1.datetime.now() - my_datetime_1.timedelta(days=365)).strftime("%Y-%m-%d")
base_url = "https://www.hltv.org"
url = base_url + "/results?offset={offset}&startDate=" + last_year + "&endDate=" + time_now + ""
div_results_all = '.results-all'
div_results = '.results'

PICKED = "picked"
REMOVED = "removed"

# BET - VPGame
vp_url = "http://www.vpgame.com/prediction/api/prediction/matches?{}"
WINNER = "Match Winner"
LIMIT = 30
params = {
    'category': "csgo",
    'limit': LIMIT,
    'status': "close",
    'order': "",
}

# Match - Upcoming
url_upcoming = base_url + "/matches"
div_match_upcoming = ".upcoming-matches"
day = 2  # get all matches upcoming in 2 next day

pinnacle = "PINNACLE"
vp_game = "VPGame"
five_etop = "5etop"

# for vp_game
vp_game_url = "https://www.vpgame.com/prediction/match/csgo/parimutuel"
div_vp_game_match_upcoming = ".prediction-match-list"

# for 5etop
five_etop_url = "https://www.5etop.com/api/match/list.do?status=run&game=csgo"
