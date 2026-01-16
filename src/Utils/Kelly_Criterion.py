def american_to_decimal(american_odds):
    """
    Converts American odds to decimal odds (European odds).
    """
    if american_odds >= 100:
        decimal_odds = (american_odds / 100) + 1
    else:
        decimal_odds = (100 / abs(american_odds)) + 1
    return round(decimal_odds, 2)

def decimal_to_american(decimal_odds: float | None):
    """
    Converts decimal odds to American odds.
    """
    if decimal_odds is None:
        return None
    if decimal_odds >= 2:
        american_odds = (decimal_odds - 1) * 100
    else:
        american_odds = -100 / (decimal_odds - 1)
    return round(american_odds, 2)

# This is jank, KC needs decimal odds -1, i want true decimal odds everywhere else
def calculate_kelly_criterion(american_odds, model_prob):
    """
    Calculates the fraction of the bankroll to be wagered on each bet using the Kelly Criterion.
    Formula: f* = (p × decimal_odds - 1) / (decimal_odds - 1)
    Returns the fraction as a percentage (0-100).
    """
    decimal_odds = american_to_decimal(american_odds)
    net_odds = decimal_odds - 1
    if net_odds <= 0:
        return 0
    bankroll_fraction = round((100 * (decimal_odds * model_prob - 1)) / net_odds, 2)
    return bankroll_fraction if bankroll_fraction > 0 else 0