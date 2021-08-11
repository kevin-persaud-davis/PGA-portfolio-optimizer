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

PROCESSED_DATA_DIR = Path(DATA_DIR, "processed")
RAW_DATA_DIR = Path(DATA_DIR, "raw")

TOURNAMENTS_DIR = Path(PROCESSED_DATA_DIR, "tournaments")

