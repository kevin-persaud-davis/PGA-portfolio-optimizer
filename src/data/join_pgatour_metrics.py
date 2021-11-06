from pathlib import Path
from os import listdir
from os.path import isfile, join
import sys
from itertools import chain
from functools import reduce


sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config

import requests
from bs4 import BeautifulSoup
import pandas as pd


def read_file(file_name, f_path):
    """Read file name from given path and create a dataframe
    
    Args:
    
    Returns:
        dataframe of file in filepath
    
    """
    # f_path_dict = {"raw_pgatour_metrics": config.RAW_PGA_METRICS_DIR,
    #             "raw_historical_player": config.RAW_HISTORICAL_DIR,}

    # f_path = f_path_dict[f_path]

    full_path = str(Path(f_path, file_name))

    df = pd.read_csv(full_path)

    drop_cols = ["RANK_THIS_WEEK", "RANK_LAST_WEEK", "ROUNDS"]

    if set(drop_cols).issubset(df.columns):
        
        df = df.drop(columns=["RANK_THIS_WEEK", "RANK_LAST_WEEK", "ROUNDS"])

    return df

def create_espn_tid_col(df):
    """create tournament id mapping for espn tournaments
    
    Args:
        df (pd.DataFrame): pgatour metrics dataframe

    Returns:
    
    """
    espn_path = str(Path(config.MAPPED_TOURNAMENTS_DIR, "mapped_tournament_ids_2017_2020.csv"))

    espn_df = pd.read_csv(espn_path)

    df_merged = pd.merge(df, espn_df,
            how="left",
            left_on=["pga_tourn_id", "pga_season_id"],
            right_on=["tournament_id_pgatour","season_id"])

    df_merged = df_merged.drop(columns=["tournament_id_pgatour", "tournament_name"])

    return df_merged


def main():
    
    mypath = str(Path(config.RAW_PGA_METRICS_DIR))

    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    frames = [read_file(f, mypath) for f in files]

    if len(files) != len(frames):
        print(f"{len(frames) - len(files)} missing files")


    df_merged = reduce(lambda left, right: pd.merge(left, right,
                                            how="outer", 
                                            on=["pga_tourn_id",
                                            "pga_season_id",
                                            "PLAYER_NAME"]), frames)


    df_merged = create_espn_tid_col(df_merged)

    # save_path = str(Path(config.PROCESSED_PGA_METRICS_DIR, "pgatour_metrics_2017_2020.csv"))

    # df_merged.to_csv(save_path)


if __name__=="__main__":

    main()