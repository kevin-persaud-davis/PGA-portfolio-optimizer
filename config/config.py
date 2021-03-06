import sys
from pathlib import Path

# Directories
BASE_DIR = Path.home()
ML_DIR = Path(BASE_DIR, "machine_learning")
PROJECT_DIR = Path(ML_DIR, "projects")
PGA_DIR = Path(PROJECT_DIR, "PGA-portfolio-optimizer")

CONFIG_DIR = Path(PGA_DIR, "config")
LOGS_DIR = Path(PGA_DIR, "logging")
MODEL_DIR = Path(PGA_DIR, "model")
DATA_DIR = Path(PGA_DIR, "data")

RAW_DATA_DIR = Path(DATA_DIR, "raw")
RAW_HISTORICAL = Path(RAW_DATA_DIR, "historical")
RAW_TOURNAMENTS_DIR = Path(RAW_DATA_DIR, "tournaments")
RAW_HISTORICAL_DIR = Path(RAW_DATA_DIR, "historical_player_data")
RAW_HISTORICAL_PRICES = Path(RAW_DATA_DIR, "historical_prices")
PGA_SEASON_2011_2016 = Path(RAW_HISTORICAL_DIR, "pga_seasons_2011_2016")
PGA_SEASON_2016 = Path(RAW_HISTORICAL_DIR, "season_2016")
PGA_SEASON_2015 = Path(RAW_HISTORICAL_DIR, "season_2015")
PGA_SEASON_2014 = Path(RAW_HISTORICAL_DIR, "season_2014")
PGA_SEASON_2013 = Path(RAW_HISTORICAL_DIR, "season_2013")
PGA_SEASON_2012 = Path(RAW_HISTORICAL_DIR, "season_2012")
PGA_SEASON_2011 = Path(RAW_HISTORICAL_DIR, "season_2011")
RAW_PGA_METRICS_DIR = Path(RAW_DATA_DIR, "pgatour_metrics_data")
RAW_PLAYER_ID_DIR = Path(RAW_DATA_DIR, "player_ids")


PROCESSED_DATA_DIR = Path(DATA_DIR, "processed")
PROCESSED_HISTORICAL = Path(PROCESSED_DATA_DIR, "historical")
TOURNAMENTS_DIR = Path(PROCESSED_DATA_DIR, "tournaments")
MAPPED_TOURNAMENTS_DIR = Path(TOURNAMENTS_DIR, "mapped_tournaments")
PROCESSED_HISTORICAL_DIR = Path(PROCESSED_DATA_DIR, "historical_player_data")
PROCESSED_PGA_METRICS_DIR = Path(PROCESSED_DATA_DIR, "pgatour_metrics_data")

FEATURES_DIR = Path(PROCESSED_DATA_DIR, "features_data")
TIMESERIES_FRAMEWORK_DIR = Path(FEATURES_DIR, "timeseries_framework")
IID_FRAMEWORK_DIR = Path(FEATURES_DIR, "iid_framework")
GROUPED_FRAMEWORK_DIR = Path(FEATURES_DIR, "grouped_framework")