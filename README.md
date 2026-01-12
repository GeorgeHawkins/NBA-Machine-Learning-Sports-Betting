# NBA Sports Betting Using Machine Learning

<img src="https://github.com/kyleskom/NBA-Machine-Learning-Sports-Betting/blob/master/Screenshots/output.png" width="1010" height="292" />

## Overview

This project predicts NBA game winners and totals (over/under) using team stats and sportsbook odds. It pulls team data from 2007-08 through the current season, builds matchup features, and runs trained models to estimate win probabilities and totals outcomes. It also outputs expected value and optional Kelly Criterion stake sizing.

## Features

- Moneyline and totals predictions (XGBoost and Neural Net models).
- Expected value calculation and optional Kelly Criterion sizing.
- Odds ingest from supported sportsbooks or manual input.
- Data processing pipeline and model training scripts.
- Flask web app for browsing outputs.

## How it works

1. **Collect stats and odds**: `Get_Data` pulls daily team stats from NBA endpoints and stores them in SQLite. `Get_Odds_Data` pulls sportsbook odds and scores from SBR and stores them in a separate SQLite DB.
2. **Build game features**: `Create_Games` merges team stats, odds, scores, and days-rest into a training dataset.
3. **Train models**: XGBoost/NN scripts in `src/Train-Models` fit moneyline and totals models.
4. **Predict today**: `main.py` fetches today’s schedule, builds matchup features, loads trained models, and prints predictions, expected value, and optional Kelly Criterion sizing.

## Requirements

- Python 3.11
- Packages: Tensorflow, XGBoost, NumPy, Pandas, Colorama, Tqdm, Requests, Scikit-learn

### Installing dependencies

**Using pip (traditional method):**

```bash
pip3 install -r requirements.txt
```

**Using uv (recommended, faster):**

```bash
# Create a virtual environment with Python 3.11
uv venv --python 3.11

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install -r requirements.txt
```

Alternatively, you can use `uv run` to automatically manage the environment:

```bash
# Install dependencies (uv will create a venv automatically)
uv pip install -r requirements.txt

# Run the app with Python 3.11
uv run --python 3.11 main.py -xgb -odds=fanduel
```

## Quick start

```bash
# With pip
python3 main.py -xgb -odds=fanduel

# With uv (if using virtual environment)
python main.py -xgb -odds=fanduel

# With uv run (no venv activation needed)
uv run --python 3.11 main.py -xgb -odds=fanduel
```

Odds will be fetched automatically when `-odds` is provided. Supported books:
`fanduel`, `draftkings`, `betmgm`, `pointsbet`, `caesars`, `wynn`, `bet_rivers_ny`

If `-odds` is omitted, the script will prompt for manual odds and totals.

Optional flags:

- `-nn` run neural network model
- `-xgb` run XGBoost model
- `-A` run all models
- `-kc` show Kelly Criterion bankroll fraction

## Flask web app

<img src="https://github.com/kyleskom/NBA-Machine-Learning-Sports-Betting/blob/master/Screenshots/Flask-App.png" width="922" height="580" />

```bash
cd Flask

# With pip
flask --debug run

# With uv (if using virtual environment)
flask --debug run

# With uv run (no venv activation needed)
uv run --python 3.11 flask --debug run
```

## Data pipeline and training

```bash
# Create/update datasets
cd src/Process-Data
# With pip: python -m Get_Data
# With uv: uv run --python 3.11 -m Get_Data
python -m Get_Data
python -m Get_Odds_Data
python -m Create_Games

# Train models
cd ../Train-Models
# With pip: python -m XGBoost_Model_ML ...
# With uv: uv run --python 3.11 -m XGBoost_Model_ML ...
python -m XGBoost_Model_ML --dataset dataset_2012-26 --trials 100 --splits 5 --calibration sigmoid
python -m XGBoost_Model_UO --dataset dataset_2012-26 --trials 100 --splits 5 --calibration sigmoid
python -m NN_Model_ML
python -m NN_Model_UO
python -m Logistic_Regression_ML --dataset dataset_2012-26_new --trials 50 --splits 5 --calibration sigmoid
python -m Logistic_Regression_UO --dataset dataset_2012-26_new --trials 50 --splits 5 --calibration sigmoid
```

### Neural network notes

- The current NN training scripts are the original versions with hard-coded dataset and model paths.
- They train on `dataset_2012-24_new` and save into `Models/` with timestamped names.
- If you want configurable flags or feature/scaler sidecars, switch back to the newer NN scripts.

### Backfilling missing data

Get_Data normally fetches only new dates in the current season. To fill missing dates:

```bash
cd src/Process-Data
# With pip: python -m Get_Data --backfill
# With uv: uv run --python 3.11 -m Get_Data --backfill
python -m Get_Data --backfill
```

To backfill a single season:

```bash
cd src/Process-Data
python -m Get_Data --backfill --season 2025-26
```

### Backfilling odds data

Get_Odds_Data normally fetches only new dates in the current season. To fill missing odds dates:

```bash
cd src/Process-Data
# With pip: python -m Get_Odds_Data --backfill
# With uv: uv run --python 3.11 -m Get_Odds_Data --backfill
python -m Get_Odds_Data --backfill
```

To backfill a single season:

```bash
cd src/Process-Data
python -m Get_Odds_Data --backfill --season 2025-26
```

## Contributing

Contributions are welcome. If you change model behavior or data pipelines, add a note in the README and update any related scripts or docs.
