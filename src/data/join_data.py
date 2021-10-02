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


    # save_path = str(Path(config.PROCESSED_PGA_METRICS_DIR, "pgatour_metrics_2017_2020.csv"))

    # df_merged.to_csv(save_path)


if __name__=="__main__":

    main()