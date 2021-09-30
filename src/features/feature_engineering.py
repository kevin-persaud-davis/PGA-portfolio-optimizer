from os import times
from pathlib import Path
import sys
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

class CombinedAttributesAdder(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        pass


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
    
def hole_scoring_percentages(p_round, score_type_1, score_type_2=None):
    """Get hole scoring percentage for a given score type. Or
    if two score types are given, find the ratio between them
    
    Args:
        p_round (series or pd.DataFrame) : player round score(s)
        
        score_type_1 (int) : shooting score type
        
        score_type_2 (int) : shooting score type, optional argument
        
    Returns:
        percentage for given scoring type(s)"""

    
    if score_type_2 is not None:
        
        s_type1_count = np.sum(np.where(p_round.values==score_type_1, 1, 0))
        s_type2_count = np.sum(np.where(p_round.values==score_type_2, 1, 0))

        if s_type2_count == 0:
            return 0
        else:
            s_percentage = np.round(s_type1_count / s_type2_count, 5)
            return s_percentage
        
    else:
        
        s_type_count = np.sum(np.where(p_round.values==score_type_1, 1, 0))
        return s_type_count / p_round.shape[0]

if __name__ == "__main__":
    
    # dk_data_path = str(Path(config.PROCESSED_HISTORICAL_DIR, "draftkings_hpd_2017_2020.csv"))
    # df = pd.read_csv(dk_data_path, parse_dates=["date"])

    # grouped_data_path = str(Path(config.GROUPED_FRAMEWORK_DIR, "features_hpd_2017_2020.csv"))
    
    # df.to_csv(grouped_data_path, index=False)
    
    # run_placing_features(df)

    # timeseries_data_path = str(Path(config.TIMESERIES_FRAMEWORK_DIR, "features_hpd_2017_2020.csv"))
    # df.to_csv(timeseries_data_path, index=False)

    timeseries_feature_path = str(Path(config.TIMESERIES_FRAMEWORK_DIR, "train_dataset_default.csv"))
    df = pd.read_csv(timeseries_feature_path, parse_dates=["date"])


    # df["made_cut"] = np.where(df["make_cut"] == True, 1, 0)
    # df["finished_r1"] = np.where(df["complete_r1"] == True, 1, 0)
    # df["finished_r2"] = np.where(df["complete_r2"] == True, 1, 0)
    # df["finished_r3"] = np.where(df["complete_r3"] == True, 1, 0)
    # df["finished_r4"] = np.where(df["complete_r4"] == True, 1, 0)


    # fantasy_hole_pt_cols = df.loc[:, "f_pts_1_1":"f_pts_4_18"].columns.tolist()


    # df["birdie_to_par_ratio"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 3, 0.5), axis=1)
    # df["birdie_to_bogey_ratio"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 3, -0.5), axis=1)
    # df["birdie_to_double_ratio"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 3, -1), axis=1)

    # df["eagle_to_par_ratio"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 8, 0.5), axis=1)
    # df["eagle_to_bogey_ratio"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 8, -0.5), axis=1)
    # df["eagle_to_double_ratio"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 8, -1), axis=1)

    # df["par_to_birdie_ratio"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 0.5, 3), axis=1)
    # df["par_to_bogey_ratio"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 0.5, -0.5), axis=1)
    # df["par_to_double_ratio"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 0.5, -1), axis=1)

    # df["eagle_pct"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 8), axis=1)
    # df["birdie_pct"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 3), axis=1)
    # df["par_pct"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, 0.5), axis=1)
    # df["bogey_pct"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, -0.5), axis=1)
    # df["double_pct"] = df[fantasy_hole_pt_cols].apply(lambda x: hole_scoring_percentages(x, -1), axis=1)

    

