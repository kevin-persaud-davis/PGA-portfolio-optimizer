from os import times
from pathlib import Path
import sys
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config

import pandas as pd
import numpy as np


def player_win_date(df):
    """Find dates of tournament wins for players
    
    Args:
        df (pd.Dataframe) : draftkings historical player data

    """
    pass

def placed_top_N(df, place_pos):
    """Days since player placed at least N or better.

    Notes:
        N is set by place

    Args:
        df (pd.Dataframe) : draftkings historical player data

        place_pos (int) : placing position in tournamnet

    Returns:
        dataframe containing last date and days since top N or better
    """
    
    df.sort_values("date", inplace=True)
    df.reset_index(inplace=True)

    org_index = df["index"].copy()
    df.drop(columns=["index"], inplace=True)

    group_N = df.groupby("player_id")

    N_placing = group_N.apply(lambda x: x.where(x["place"] <= place_pos).ffill())
    N_placing.rename(columns={"date":f"last_top_{place_pos}"}, inplace=True)
    N_placing["index"] = org_index

    n_df = df.join(N_placing[["index", f"last_top_{place_pos}"]]).copy()

    n_df[f"days_since_top_{place_pos}"] = n_df["date"] - n_df[f"last_top_{place_pos}"]
    n_df.set_index("index", inplace=True)

    return n_df

def last_win(df):
    """Days since player last win
    
    Notes:
        df should only be a subset of entire draftkings historical player data

    Args:
        df (pd.dataframe): draftkings historical player data

    Returns:
        dataframe containing last win date and days since last win
    """
    df.sort_values("date", inplace=True)
    df.reset_index(inplace=True)

    org_index = df["index"].copy()
    df.drop(columns=["index"], inplace=True)

    
    group_wins = df.groupby("player_id")
    wins = group_wins.apply(lambda x: x.where(x.place == 1).ffill())

    wins.reset_index(inplace=True)
    wins.rename(columns={"date":"last_win"}, inplace=True)
    
    wins["index"] = org_index
    n_df = df.join(wins[["index", "last_win"]])

    n_df["days_since_win"] = n_df["date"] - n_df["last_win"]

    n_df.set_index("index", inplace=True)
    
    return n_df

def run_placing_features(df, feat_dir=None, fname=None):
    """Create placing features from 1st to 50th by 2 place increments
    
    Args:
        df (pd.Dataframe) : draftkings historical player data

        feat_dir (str) : features framework directory

        fname (str) : file name
    """

    for i in range(1, 51, 2):
        sub_df = df[["player_id", "tournament_id", "place", "date"]].copy()
        if i == 1:
            place_date_df = last_win(sub_df)

            df["last_win"] = place_date_df["last_win"]
            df["days_since_win"] = place_date_df["days_since_win"]
        else:
            place_date_df = placed_top_N(sub_df, i)

            df[f"last_top_{i}"] = place_date_df[f"last_top_{i}"]
            df[f"days_since_top_{i}"] = place_date_df[f"days_since_top_{i}"]

    # if feat_dir.lower() == "timeseries":

    # if fname is not None:
    
    #     features_data_path = str(Path(config.FEATURES_DIR, fname))
    #     df.to_csv(features_data_path, index=False)
        


if __name__ == "__main__":
    
    dk_data_path = str(Path(config.PROCESSED_HISTORICAL_DIR, "draftkings_hpd_2017_2020.csv"))
    df = pd.read_csv(dk_data_path, parse_dates=["date"])

    iid_data_path = str(Path(config.IID_FRAMEWORK_DIR, "features_hpd_2017_2020.csv"))
    
    df.to_csv(iid_data_path, index=False)

    run_placing_features(df)

    timeseries_data_path = str(Path(config.TIMESERIES_FRAMEWORK_DIR, "features_hpd_2017_2020.csv"))
    df.to_csv(timeseries_data_path, index=False)
    

