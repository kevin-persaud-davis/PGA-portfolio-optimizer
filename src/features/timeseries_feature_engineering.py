from pathlib import Path
import sys
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit


def split_dataset(df, t_gap=0, t_size=None):
    """Split dataset using based on TimeSeriesSplit framework
    
    Args:
        df (pd.DataFrame) : historical features dataset (base/non-modified)
        
        t_gap (int) : period of gaps between train and test set split
        
        t_size (int) : default of n_samples // (n_splits + 1), maximum allowed
        
    Returns:
        TimeSeriesSplit of training and test set based on given parameters
    """
    df.sort_values(by="date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    tscv = TimeSeriesSplit(gap=t_gap, test_size=t_size)

    for train_index, test_index in tscv.split(df):
        ts_train_set = df.loc[train_index]
        ts_test_set = df.loc[test_index]

    return ts_train_set, ts_test_set
    


if __name__ == "__main__":

    ts_features_datapath = str(Path(config.TIMESERIES_FRAMEWORK_DIR, "features_hpd_2017_2020.csv"))
    df = pd.read_csv(ts_features_datapath, parse_dates=["date"])

    train_df, test_df = split_dataset(df)

    timeseries_train_dataset = str(Path(config.TIMESERIES_FRAMEWORK_DIR, "train_dataset_default.csv"))

    timeseries_test_dataset = str(Path(config.TIMESERIES_FRAMEWORK_DIR, "test_dataset_default.csv"))

    train_df.to_csv(timeseries_train_dataset, index=False)
    test_df.to_csv(timeseries_test_dataset, index=False)
