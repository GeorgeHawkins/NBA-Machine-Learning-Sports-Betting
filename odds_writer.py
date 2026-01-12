import subprocess, re
import json
import gspread
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

def fetch_game_data(sportsbook="fanduel"):
    cmd = ["python", "main.py", "-xgb", f"-odds={sportsbook}"]
    stdout = subprocess.check_output(cmd).decode()
    data_re = re.compile(r'\n(?P<home_team>[\w ]+)(\((?P<home_confidence>[\d+\.]+)%\))? vs (?P<away_team>[\w ]+)(\((?P<away_confidence>[\d+\.]+)%\))?: (?P<ou_pick>OVER|UNDER) (?P<ou_value>[\d+\.]+) (\((?P<ou_confidence>[\d+\.]+)%\))?', re.MULTILINE)
    ev_re = re.compile(r'(?P<team>[\w ]+) EV: (?P<ev>[-\d+\.]+)', re.MULTILINE)
    odds_re = re.compile(r'(?P<away_team>[\w ]+) \((?P<away_team_odds>-?\d+)\) @ (?P<home_team>[\w ]+) \((?P<home_team_odds>-?\d+)\)', re.MULTILINE)
    games = []
    for match in data_re.finditer(stdout):
        game_dict = {'away_team': match.group('away_team').strip(),
                     'home_team': match.group('home_team').strip(),
                     'home_confidence': match.group('home_confidence'),
                     'ou_pick': match.group('ou_pick'),
                     'ou_value': match.group('ou_value'),
                     'ou_confidence': match.group('ou_confidence')}
        for ev_match in ev_re.finditer(stdout):
            if ev_match.group('team') == game_dict['away_team']:
                game_dict['away_team_ev'] = ev_match.group('ev')
            if ev_match.group('team') == game_dict['home_team']:
                game_dict['home_team_ev'] = ev_match.group('ev')
        for odds_match in odds_re.finditer(stdout):
            if odds_match.group('away_team') == game_dict['away_team']:
                game_dict['away_team_odds'] = odds_match.group('away_team_odds')
            if odds_match.group('home_team') == game_dict['home_team']:
                game_dict['home_team_odds'] = odds_match.group('home_team_odds')

        games.append(game_dict)
    return games


def write_game_data(games):

    gc = gspread.service_account(filename='service-account.json')
    sheet = gc.open_by_key(os.getenv('GOOGLE_SHEETS_KEY'))
    all_games_worksheet = sheet.worksheet('All Games')
    ml_worksheet = sheet.worksheet('ML')
    ou_worksheet = sheet.worksheet('OU')
    
    all_games_new_rows = []
    # might just reference (count if?) the main sheet for the actual ml and ou sheets
    # ml_new_rows = []
    # ou_new_rows = []

    for game in games:
        all_games_row = [datetime.datetime.now().strftime('%Y-%m-%d'), game['home_team'], float(game['home_team_ev']), float(game['home_confidence']) / 100, game['away_team'], float(game['away_team_ev']), game['ou_pick'], float(game['ou_value']), float(game['ou_confidence'])]
        # ml_row = [datetime.datetime.now().strftime('%Y-%m-%d'), game['home_team'], float(game['home_team_ev']), float(game['home_confidence']) / 100, game['away_team'], float(game['away_team_ev']), game['ou_pick'], float(game['ou_value']), float(game['ou_confidence'])]
        # ou_row = [datetime.datetime.now().strftime('%Y-%m-%d'), game['home_team'], float(game['home_team_ev']), float(game['home_confidence']) / 100, game['away_team'], float(game['away_team_ev']), game['ou_pick'], float(game['ou_value']), float(game['ou_confidence'])]
        all_games_new_rows.append(all_games_row)

    all_games_worksheet.append_rows(all_games_new_rows)
    

    print(json.dumps(games, sort_keys=True, indent=4))

games = fetch_game_data()

write_game_data(games)