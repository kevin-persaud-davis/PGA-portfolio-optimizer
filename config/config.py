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
RAW_HISTORICAL_DIR = Path(RAW_DATA_DIR, "historical_player_data")
RAW_PGA_METRICS_DIR = Path(RAW_DATA_DIR, "pgatour_metrics_data")


PROCESSED_DATA_DIR = Path(DATA_DIR, "processed")

TOURNAMENTS_DIR = Path(PROCESSED_DATA_DIR, "tournaments")
PROCESSED_HISTORICAL_DIR = Path(PROCESSED_DATA_DIR, "historical_player_data")

FEATURES_DIR = Path(PROCESSED_DATA_DIR, "features_data")
TIMESERIES_FRAMEWORK_DIR = Path(FEATURES_DIR, "timeseries_framework")
IID_FRAMEWORK_DIR = Path(FEATURES_DIR, "iid_framework")
