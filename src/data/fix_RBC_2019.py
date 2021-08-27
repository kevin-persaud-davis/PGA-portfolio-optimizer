from datetime import date
from pathlib import Path
import sys
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")

import config
import pandas as pd
import numpy as np

def input_rbc_open_19(df):
    """Input missing data for rbc canadian open 2019

    Args:
        df (pd.Dataframe) : historical player data for RBC canadian open 2019

    """

    # missing data to be entered into df
    rbc_canadian_open_2019 = {
    "3470": [3,4,4,5,3,3,4,2,4,
            4,3,4,3,4,3,3,4,4],
    "4587": [4,5,4,4,4,3,3,2,3,
            4,4,3,3,4,4,3,5,4],
    "1614": [4,4,4,5,4,3,3,3,4,
            4,3,3,3,4,4,3,5,4],
    "1222": [4,4,3,5,4,3,4,4,3,
            4,4,4,3,4,3,4,5,4],
    "257": [4,4,5,4,3,3,4,3,4,
            4,3,4,3,4,5,3,5,4],
    "5548": [4,5,4,5,3,3,4,3,4,
            4,4,4,2,4,3,3,4,4],
    "11382": [5,4,4,5,4,4,4,3,4,
            4,4,4,4,4,5,3,4,4],
    "4304": [3,4,4,5,4,4,4,5,4,
            3,4,4,3,4,4,2,4,4],
    "301": [3,6,4,5,4,3,4,3,5,
            3,4,4,3,4,3,3,5,4],
    "576": [4,3,4,4,5,3,4,3,4,
            5,4,3,4,4,3,3,4,4],
    "10404": [5,4,4,5,5,3,4,3,5,
            4,5,4,2,3,3,3,4,4],
    "4645": [4,4,3,6,4,2,5,2,5,
            3,4,4,3,5,4,3,4,4],
    "6185": [5,4,4,4,4,3,3,3,5,
            4,4,4,3,3,5,3,4,4],
    "508": [3,4,4,4,4,3,3,3,4,
            3,4,4,3,3,4,3,4,4],
    "6931": [4,5,4,4,3,3,4,3,4,
            4,4,4,4,3,4,3,5,4],
    "6937": [4,4,4,4,4,3,4,3,4,
            4,4,4,3,5,4,3,5,5],
    "11387": [5,4,3,4,4,4,4,4,4,
            3,4,3,3,5,5,4,4,4],
    "10592": [4,5,4,5,4,3,4,4,3,
            4,3,3,2,4,4,3,5,5],
    "3669": [4,4,5,5,4,4,4,4,3,
            5,4,4,3,4,4,3,4,3],
    "10831": [4,4,5,4,3,4,3,3,4,
            4,4,4,3,3,4,3,4,4],
    "5408": [4,3,5,5,4,4,4,3,4,
            4,4,3,3,4,4,3,4,4],
    "3448": [4,4,4,4,4,3,5,3,5,
            4,3,4,2,4,4,3,4,4],
    "3950": [5,3,4,5,3,3,5,3,3,
            4,4,4,3,4,4,2,4,4],
    "8910": [4,4,4,6,4,4,4,2,4,
            4,4,4,3,5,5,3,4,4],
    "4848": [4,4,3,4,3,4,4,3,3,
            4,4,4,4,4,5,3,5,4],
    "9364": [5,3,4,4,4,4,4,3,4,
            5,5,3,3,4,3,2,4,4],
    "4015": [5,3,4,3,5,3,4,3,4,
            4,4,4,4,4,4,3,4,5],
    "153": [4,4,3,5,4,4,4,2,5,
            3,5,3,3,3,4,3,4,4],
    "9571": [3,4,4,7,4,3,3,3,4,
            4,3,4,3,4,5,3,4,5],
    "3792": [5,4,3,5,4,3,4,3,4,
            4,5,6,4,4,4,3,4,4],
    "4591": [4,4,4,5,4,3,4,4,4,
            4,4,4,5,4,3,4,4,4],
    "5692": [4,4,3,5,4,3,4,2,3,
            4,5,3,3,5,4,3,5,5],
    "11099": [3,4,4,4,4,4,3,3,4,
            4,4,4,3,4,4,4,4,4],
    "3279": [4,4,5,4,3,4,4,3,4,
            4,5,4,3,5,4,3,4,4],
    "9025": [4,4,4,5,4,3,4,3,4,
            5,4,4,3,3,4,3,4,4],
    "3740": [5,4,4,5,4,3,4,2,4,
            3,4,5,3,3,4,3,5,4],
    "9513": [4,4,4,4,4,4,4,3,4,
            5,5,4,3,4,4,3,4,4],
    "686": [3,3,4,5,5,4,4,3,4,
            3,5,3,3,4,5,3,4,5],
    "962": [4,3,4,5,4,4,4,4,4,
            3,4,4,3,5,4,3,6,4],
    "335": [4,4,5,4,4,3,4,3,4,
            4,4,4,3,4,4,3,4,4],
    "5619": [4,4,4,5,4,2,5,3,4,
            4,3,4,3,5,4,2,5,4],
    "6991": [3,5,4,4,5,3,4,4,4,
            5,4,4,3,4,4,2,5,4],
    "446": [4,4,4,4,4,3,4,3,4,
            4,4,4,3,4,4,3,5,6],
    "3856": [3,4,4,6,4,3,5,4,4,
            4,4,4,3,4,4,2,4,4],
    "4513": [4,4,4,4,4,3,6,3,4,
            4,3,5,3,4,4,3,5,5],
    "693": [4,4,5,5,6,4,3,3,4,
            4,3,3,3,4,4,3,5,4],
    "10166": [4,5,5,4,4,3,3,2,4,
            4,4,3,3,5,3,3,5,5],
    "3793": [6,6,4,6,4,3,3,3,4,
            4,4,4,3,4,4,3,4,5],
    "1674": [4,4,3,4,3,4,4,3,4,
            4,3,4,4,4,3,3,5,4],
    "8971": [4,4,4,6,4,3,4,3,4,
            4,5,4,2,4,4,4,4,5],
    "1225": [4,4,4,5,4,3,4,4,4,
            3,4,5,3,5,3,3,4,5],
    "1793": [3,6,4,5,4,3,4,3,5,
            4,4,4,2,4,3,3,4,4],
    "6798": [5,5,5,5,3,4,4,3,4,
            4,3,4,3,4,4,3,5,4],
    "2571": [4,4,4,5,4,3,5,3,4,
            4,4,3,3,4,4,4,5,5],
    "5506": [4,4,4,4,4,3,4,4,5,
            4,4,4,3,4,5,2,4,4],
    "6894": [4,4,4,5,5,2,4,4,4,
            4,3,3,4,3,4,3,5,6],
    "10372": [4,3,5,5,4,3,4,5,4,
            4,4,5,3,3,4,3,5,5],
    "6090": [4,3,5,5,4,4,4,3,4,
            4,4,3,3,3,4,3,4,4],
    "5167": [5,5,4,4,4,3,4,3,4,
            6,4,4,4,5,4,3,5,4],
    "9569": [4,5,4,4,4,3,4,3,4,
            4,4,5,4,5,5,3,5,4],
    "808": [5,4,4,5,5,3,4,3,5,
            4,4,3,4,4,4,3,5,3],
    "8961": [5,4,3,6,4,3,4,3,4,
            4,4,4,4,4,5,2,5,4],
    "159": [5,4,5,4,5,4,4,3,4,
            4,4,4,3,5,4,3,4,4],
    "3832": [5,4,4,5,4,3,4,3,4,
            5,4,4,4,4,4,4,4,4],
    "1568": [4,4,4,4,3,4,4,4,4,
            4,4,4,4,4,4,3,5,5],
    "431": [5,5,4,5,4,3,4,4,5,
            4,4,5,3,5,4,3,4,4],
    "780": [5,4,4,4,4,3,4,3,5,
            3,5,6,3,5,4,3,4,4],
    "8992": [4,4,6,6,4,4,5,4,4,
            4,3,4,3,3,4,4,6,5],
    "10163": [3,5,6,4,3,3,4,3,5,
            5,6,5,2,4,4,3,5,5],
    "9843": [4,4,5,5,4,4,4,3,4,
            4,4,5,4,5,4,3,5,4],
    "6689": [4,5,5,5,4,4,4,4,5,
            4,5,4,3,5,4,2,5,4],
    }

    input_df = pd.DataFrame(rbc_canadian_open_2019)
    input_df = input_df.T

    round_3_cols = [f"round_3_{i}" for i in range(1,19)]
    round_3_cols.insert(0,"player_id")
    input_df.reset_index(inplace=True)
    
    
    assert len(input_df.columns) == len(round_3_cols)
    # rename columns to match df columns
    input_df.columns = round_3_cols

    
    # make column same type as df
    input_df["player_id"] = pd.to_numeric(input_df["player_id"])

    # sort both dataframes by player_id for future merge
    input_df.sort_values(by=["player_id"], inplace=True)
    df.sort_values(by=["player_id"], inplace=True)
    
    sorted_index = df.index
    input_df["merge_index"] = sorted_index
    input_df.set_index("merge_index", inplace=True)

    df[round_3_cols] = input_df


def hole_point_score(hole_score):
    """Calculate point score for a given hole
    
    Args:
        hole_score (pd.Series) : player hole scores

    Returns:
        point score mapping for holes
    """
    pt_score_dict = {-2 : "eagle", -1 : "birdie", 0 : "par", 1 : "bogey", 2 : "double",}

    pt_map_df = pd.DataFrame(list(pt_score_dict.items()), columns=["diff", "shot_score"])

    condition_list = [hole_score == pt_map_df["diff"][0], 
                    hole_score == pt_map_df["diff"][1],
                    hole_score == pt_map_df["diff"][2],
                    hole_score == pt_map_df["diff"][3],
                    hole_score <= pt_map_df["diff"][4]]

    condition_choice = [pt_map_df["shot_score"][0],
                    pt_map_df["shot_score"][1],
                    pt_map_df["shot_score"][2],
                    pt_map_df["shot_score"][3],
                    pt_map_df["shot_score"][4]]

    return np.select(condition_list, condition_choice)

def rbc_pts_mapping(df):
    """Fill rd 3 points through shot difference mapping

    Args:
        df (pd.Dataframe) : historical player data for RBC canadian open 2019

    Returns:
        rd_3_pts (pd.Dataframe) : round 3 hole scores

        pts_col (list) : round 3 columns
    """
    rbc_par_scores = {
        "hole_1" : 4,
        "hole_2" : 4,
        "hole_3" : 4,
        "hole_4" : 5,
        "hole_5" : 4,
        "hole_6" : 3,
        "hole_7" : 4,
        "hole_8" : 3,
        "hole_9" : 4,
        "hole_10" : 4,
        "hole_11" : 4,
        "hole_12" : 4,
        "hole_13" : 3,
        "hole_14" : 4,
        "hole_15" : 4,
        "hole_16" : 3,
        "hole_17" : 5,
        "hole_18" : 4,
    }
    
    rbc_par_df = pd.DataFrame.from_dict(rbc_par_scores, orient="index").T

    rd_3_pts = df - rbc_par_df.values
    
    rd_3_pts = rd_3_pts.apply(lambda x: hole_point_score(x))
    rd_3_pts = rd_3_pts.add_suffix("_pts")

    pts_col = rd_3_pts.columns.tolist()
    
    return rd_3_pts, pts_col

def fix_rbc_2019():
    """Fix missing data errors from espn for RBC canadian open

    """
    historical_data_path = str(Path(config.PROCESSED_HISTORICAL_DIR, "hpd_2017_2020.csv"))
    player_df = pd.read_csv(historical_data_path, parse_dates=["date"])

    missing_rbc = player_df[(player_df.round_4_1.isnull().values == False) & (player_df.tournament_id == 401056555)].copy()
    
    input_rbc_open_19(missing_rbc)
    round_3_cols = [f"round_3_{i}" for i in range(1,19)]
    round_3_cols.insert(0,"player_id")

    missing_pts_df, missing_pts_cols = rbc_pts_mapping(missing_rbc[round_3_cols[1:]])
    missing_pts_df.sort_index(inplace=True)
    missing_rbc.sort_index(inplace=True)

    missing_rbc[missing_pts_cols] = missing_rbc[missing_pts_cols].fillna(missing_pts_df)
    # update original df to reflect changes

    player_df[(player_df.round_4_1.isnull().values == False) & (player_df.tournament_id == 401056555)] = missing_rbc
    
    player_df.to_csv(historical_data_path, index=False)
    

if __name__ == "__main__":

    fix_rbc_2019()