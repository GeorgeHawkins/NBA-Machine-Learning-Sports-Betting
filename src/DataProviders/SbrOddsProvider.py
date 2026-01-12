from sbrscrape import Scoreboard
import json

class SbrOddsProvider:
    """ Abbreviations dictionary for team location which are sometimes saved with abbrev instead of full name.
    Moneyline options name require always full name
    Returns:
        string: Full location name
    """

    def __init__(self, sportsbook="fanduel"):
        sb = Scoreboard(sport="NBA")
        self.games = sb.games if hasattr(sb, 'games') else []
        self.sportsbook = sportsbook

    def get_odds(self):
        """Function returning odds from Sbr server's json content

        Returns:
            dictionary: [home_team_name + ':' + away_team_name: { home_team: money_line_odds, away_team: money_line_odds }, under_over_odds: val]
        """
        dict_res = {}
        for game in self.games:
            # Get team names
            home_team_name = game['home_team'].replace("Los Angeles Clippers", "LA Clippers")
            away_team_name = game['away_team'].replace("Los Angeles Clippers", "LA Clippers")

            money_line_home_value = money_line_away_value = totals_value = unders_value = overs_value = None

            # Get money line bet values
            if self.sportsbook in game['home_ml']:
                money_line_home_value = game['home_ml'][self.sportsbook]
            if self.sportsbook in game['away_ml']:
                money_line_away_value = game['away_ml'][self.sportsbook]

            # Get totals bet value
            # print("------------------GAME--------------------------------")
            # print(json.dumps(game, sort_keys=True, indent=4))
            if self.sportsbook in game['total']:
                totals_value = game['total'][self.sportsbook]

            if self.sportsbook in game['under_odds']:
                unders_value = game['under_odds'][self.sportsbook]
            if self.sportsbook in game['over_odds']:
                overs_value = game['over_odds'][self.sportsbook]

            dict_res[home_team_name + ':' + away_team_name] = {
                'under_over_line': totals_value,
                'under_odds': unders_value,
                'over_odds': overs_value,
                home_team_name: {'money_line_odds': money_line_home_value},
                away_team_name: {'money_line_odds': money_line_away_value}
            }
        return dict_res
