import requests
from typing import Any, List, TypedDict, Optional
from datetime import datetime
from src.Utils.Kelly_Criterion import decimal_to_american
from enum import Enum

# https://www.sportsbet.com.au/apigw/sportsbook-sports/Sportsbook/Sports/Competitions/6927?displayType=default&includeTopMarkets=true&eventFilter=matches



class LiveStreamingInfo(TypedDict):
    providerName: str
    streamStartTime: int
    streamTypes: List[str]

class StatusCode(Enum):
    A = "A"
    EMPTY = "-"
    H = "H"
    L = "L"


class MarketSort(Enum):
    EMPTY = "--"
    HH = "HH"
    HL = "HL"
    WH = "WH"


class Price(TypedDict):
    winPrice: float
    winPriceNum: int
    winPriceDen: int
    priceCode: StatusCode
    topicLink: str

class Selection(TypedDict):
    id: int
    name: str
    resultType: StatusCode
    externalId: int
    sort: int
    statusCode: StatusCode
    price: Price
    topicLink: str
    outcomeVariants: List[Any]
    multiplesKey: Optional[str]
    unformattedHandicap: Optional[str]
    displayHandicap: Optional[str]

class MarketList(TypedDict):
    id: int
    externalId: int
    name: str
    statusCode: StatusCode
    sort: int
    marketType: StatusCode
    marketSort: MarketSort
    bir: bool
    powerPlay: bool
    mbsAvailable: bool
    cashoutAvailable: bool
    sgmCashoutAvailable: Optional[bool]
    eachwayAvailable: bool
    topicLink: str
    selections: List[Selection]
    sameGameMultiEnabled: bool
    sameGameMultiExpanded: bool
    sameMarketMultiEnabled: bool
    samePodiumMultiEnabled: bool
    accMax: int
    accRestriction: StatusCode
    geolocationExclusion: List[Any]
    mbs: bool
    displayOrder: int
    blurb: Optional[str]

class Event(TypedDict):
    id: int
    name: str
    className: str
    competitionId: int
    competitionName: str
    startTime: int
    hasBir: bool
    hasBirStarted: bool
    eventSort: str
    numMarkets: int
    liveStream: bool
    liveStreamingInfo: List[LiveStreamingInfo]
    powerPlay: bool
    bettingStatus: str
    participant1: str
    participant2: str
    vs: str
    classId: int
    personalisedMarketsEnabled: bool
    displayName: str
    externalId: int
    statusCode: StatusCode
    sort: int
    featuredEvent: bool
    birPriority: bool
    streamingAvailable: bool
    mbsAvailable: bool
    isDisplayed: bool
    topicLink: str
    httpLink: str
    competitionExternalId: int
    classExternalId: int
    sameGameMultiEnabled: bool
    isFuture: bool
    geolocationExclusion: List[Any]
    marketList: List[MarketList]
    liveTopicLink: Optional[str]

class SportsBetResponse(TypedDict):
    id: int
    name: str
    classId: int
    className: str
    powerPlay: bool
    startTime: int
    hasBir: bool
    mbsAvailable: bool
    topicLink: str
    events: List[Event]

def fetch_odds() -> SportsBetResponse:
    us_nba_id = 6927
    url = f"https://www.sportsbet.com.au/apigw/sportsbook-sports/Sportsbook/Sports/Competitions/{us_nba_id}?displayType=default&includeTopMarkets=true&eventFilter=matches"
    response = requests.get(url)
    return response.json()

class SportsbetOddsProvider:
    def __init__(self, date):
        self.date = date
        self.odds = fetch_odds()

    def get_odds(self):

        games = self.odds["events"]

        dict_res = {}

        for game in games:
            timestamp_ms = game["startTime"]
            game_date = datetime.fromtimestamp(timestamp_ms)
            filter_date = datetime.strptime(self.date, "%m/%d/%Y")
            # if the game date does not match the filter date, skip the game
            if game_date.date() != filter_date.date():
                continue
            home_team_name = game['participant2'].replace("Los Angeles Clippers", "LA Clippers")
            away_team_name = game['participant1'].replace("Los Angeles Clippers", "LA Clippers")

            money_line_home_value = money_line_away_value = totals_value = unders_value = overs_value = None

            match_betting_market = next((market for market in game["marketList"] if market["name"] == "Match Betting"), None)
            total_points_market = next((market for market in game["marketList"] if market["name"] == "Total Points"), None)

            # Safely extract money line values, defaulting to None if market or selections don't exist
            if match_betting_market and match_betting_market.get("selections") and len(match_betting_market["selections"]) >= 2:
                money_line_away_value = match_betting_market["selections"][0].get("price", {}).get("winPrice")
                money_line_home_value = match_betting_market["selections"][1].get("price", {}).get("winPrice")
            else:
                money_line_away_value = None
                money_line_home_value = None

            if total_points_market and total_points_market.get("selections") and len(total_points_market["selections"]) >= 2:
                totals_value = total_points_market["selections"][0].get("unformattedHandicap")
                overs_value = total_points_market["selections"][0].get("price", {}).get("winPrice")
                unders_value = total_points_market["selections"][1].get("price", {}).get("winPrice")
            else:
                totals_value = None
                overs_value = None
                unders_value = None

            dict_res[home_team_name + ':' + away_team_name] = {
                    'under_over_line': float(totals_value),
                    'under_odds': decimal_to_american(unders_value),
                    'over_odds': decimal_to_american(overs_value),
                    home_team_name: {'money_line_odds': decimal_to_american(money_line_home_value)},
                    away_team_name: {'money_line_odds': decimal_to_american(money_line_away_value)}
                }

        return dict_res