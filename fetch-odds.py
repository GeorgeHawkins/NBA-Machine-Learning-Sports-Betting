import requests
from typing import Dict, Any, List, TypedDict
from datetime import datetime

# https://www.sportsbet.com.au/apigw/sportsbook-sports/Sportsbook/Sports/Competitions/6927?displayType=default&includeTopMarkets=true&eventFilter=matches

from typing import List, Any, Optional
from enum import Enum


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

def print_market_odds(market: MarketList):
    print("*******************************")
    print(market["name"])
    print("*******************************")
    for selection in market["selections"]:
        print(selection["name"])
        print(selection["price"]["winPrice"])
        if selection["name"] == "Over" or selection["name"] == "Under":
            print(selection["unformattedHandicap"])


odds = fetch_odds()

for event in odds["events"]:
    print("--------------------------------")
    print(event["name"])
    timestamp_ms = event["startTime"]
    dt = datetime.fromtimestamp(timestamp_ms)
    print(dt.strftime("%Y-%m-%d %H:%M:%S %Z"))
    print("--------------------------------")
    match_betting_market = next((market for market in event["marketList"] if market["name"] == "Match Betting"), None)
    total_points_market = next((market for market in event["marketList"] if market["name"] == "Total Points"), None)
    print_market_odds(match_betting_market)
    print_market_odds(total_points_market)