from pathlib import Path, PurePath
import os
from fnmatch import fnmatch
import sys
import csv

sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config
from pgatour_metrics import get_espn_tournaments

import time
from csv import DictWriter
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import wraps

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

def timeit(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = method(*args, **kwargs)
        end_time = time.time()
        print(f"{method.__name__} => {(end_time-start_time)*1000} ms")

        return result
    
    return wrapper

def find_player_id(player):
    """Find player id

    Args:
        player (str) : tournament participant

    Returns:
        player id
    """
    id_ = "id/"
    beg = player.find(id_) + len(id_)
    end = player.rfind("/")

    return player[beg:end]

def get_player_ids(t_body):
    """
    All player id's from tournament

    """
    # scorecard_beg = "https://www.espn.com/golf/player/scorecards/_/id/"
    player_ids = []
    players = t_body.find_all("tr", class_="Table__TR Table__even")
    if players is not None:
        for player in players:
            p_id_link = player.find("a")
            # ensure that espn has player links on page
            # if not, there is no player information
            if p_id_link is not None:
                p_id = find_player_id(p_id_link["href"])
                player_ids.append(p_id)
    return player_ids

def missing_data(scoring_data):
    """Fill missing hole entries

    Args:
        scoring_data (list) : round data with missing entries

    Returns:
        scoring_data (list) : round data filled
    """
    missing_holes = 9 - len(scoring_data)
    missing_entries = [None] * missing_holes
    scoring_data.extend(missing_entries)
    assert len(scoring_data) == 9

    return scoring_data

def missing_round(rd_name):
    """Fills missing round for player with None entires.

    Args:
        rd_name (str) : tournament round number
    
    Returns:
        data (dict) : tournament round shot score data.

        data_pts (dict) : tournament round hole score data.
    
    """
    hole_ids = [rd_name + "_" + str(hn) for hn in range(1,19)]
    hole_pts_id = [h_id + "_pts" for h_id in hole_ids]

    hole_data = [None] * 18
    hole_data_pts = [None] * 18

    data = dict(zip(hole_ids, hole_data))
    data_pts = dict(zip(hole_pts_id, hole_data_pts))
    
    return data, data_pts

def find_rd_number(rd):
    """Find round number for scorecard
    
    Args:
        rd (element.Tag) : div.roundSwap active. id attr
                        includes round number

    Returns:
        tournament round number
    """
    rd_name = rd["id"]
    rd_name = rd_name[:rd_name.rfind("-")]
    rd_name = rd_name.replace("-", "_")
    return rd_name

def missing_round_number(scoring_base):
    """Find missing round number(s) of player during tournament.
    Ensures that same round number is not used twice.

    Args:

        scoring_base (ResultSet) :  set of player tournament rounds

    Returns:

        m_rx : missing round name (x - dependent of number of rounds missed)

    """
    rd_check = np.array(["round_1", "round_2", "round_3", "round_4"])

    if len(scoring_base) == 1:
        rd_z = np.array([find_rd_number(scoring_base[0])])
        missing_rds = np.setdiff1d(rd_check, rd_z)
        
        assert len(missing_rds) == 3
        m_r1 = missing_rds[0]
        m_r2 = missing_rds[1]
        m_r3 = missing_rds[2]

        return m_r1, m_r2, m_r3

    elif len(scoring_base) == 2:
        rd_z = find_rd_number(scoring_base[0])
        rd_y = find_rd_number(scoring_base[1])
        
        rds = np.array([rd_z, rd_y])

        missing_rds = np.setdiff1d(rd_check, rds)

        assert len(missing_rds) == 2
        m_r1 = missing_rds[0]
        m_r2 = missing_rds[1]

        return m_r1, m_r2
        

    elif len(scoring_base) == 3:
        rd_z = find_rd_number(scoring_base[0])
        rd_y = find_rd_number(scoring_base[1])
        rd_x = find_rd_number(scoring_base[2])

        rds = np.array([rd_z, rd_y, rd_x])

        missing_rds = np.setdiff1d(rd_check, rds)

        assert len(missing_rds) == 1
        m_r1 = missing_rds[0]
        
        return m_r1

    else:
        print("Incorrect number of rounds given.\n")


def get_round_scores(rd):
    """Get player scores, both shot and hole data, for 9 holes

    Args:
        rd (list) : player 9 hole scoring data
    
    Returns:
        shot_data (list) : shot data for 9 holes

        hole_data (list) : hole data for 9 holes 

    """

    shot_data = [int(score.text) if score.text else None for score in rd ]
    hole_data = [score["class"][0] if score["class"][0] != "textcenter" else None for score in rd]

    if len(shot_data) != 9:
        
        shot_data = missing_data(shot_data)
    
    if len(hole_data) != 9:

        hole_data = missing_data(hole_data)

    return shot_data, hole_data


def round_data(round_base, rd_name):
    """Get player data for specific round in tournament

    Args:
        round_base (element.Tag) : tournament round data
    
    Returns:
        data (dict) : tournament round shot score data. item entries 
                    contain ints to reflect scoring data

        data_pts (dict) : tournament round hole score data. item entries
                    contain strs to reflect scoring data

    """
    front_hole_ids = [rd_name + "_" + str(hn) for hn in range(1,10)]
    back_hole_ids = [rd_name + "_" + str(hn) for hn in range(10, 19)]
    
    front_pts_id = [h_id + "_pts" for h_id in front_hole_ids]
    back_pts_id = [h_id + "_pts" for h_id in back_hole_ids]
    
    rd_body = round_base.find_all("tr", class_="oddrow")
    
    rd_front_total = rd_body[-2].find_all("td", class_="textcenter")
    
    rd_back_total = rd_body[-1].find_all("td", class_="textcenter")
    
    if len(rd_front_total) == 10:
        # Disregard totals
        rd_front = rd_front_total[:-1]
        
        front_shot_data, front_hole_data = get_round_scores(rd_front)

        f_labeled_data = dict(zip(front_hole_ids, front_shot_data)) 
        f_labeled_data_pts = dict(zip(front_pts_id, front_hole_data))
        
    else:
        rd_front = rd_front_total
        front_shot_data, front_hole_data = get_round_scores(rd_front)
        
        f_labeled_data = dict(zip(front_hole_ids, front_shot_data))
        f_labeled_data_pts = dict(zip(front_pts_id, front_hole_data))

    if len(rd_back_total) == 10:
        rd_back = rd_back_total[:-1]
        
        back_shot_data, back_hole_data = get_round_scores(rd_back)

        b_labeled_data = dict(zip(back_hole_ids, back_shot_data))
        b_labeled_data_pts = dict(zip(back_pts_id, back_hole_data))
        
    else:
        rd_back = rd_back_total
        back_shot_data, back_hole_data = get_round_scores(rd_back)
        
        b_labeled_data = dict(zip(back_hole_ids, back_shot_data))
        b_labeled_data_pts = dict(zip(back_pts_id, back_hole_data))
    
    
    data = {**f_labeled_data, **b_labeled_data}
    data_pts = {**f_labeled_data_pts, **b_labeled_data_pts}

    return data, data_pts

def scoring_data(scoring_base):
    """Get player scoring data for each round in tournament

    Args:
        scoring_base (ResultSet) : set of player tournament rounds. Length
                            reflects number of rounds played in tournament.
    
    Returns:
        round data containing player id, tourn id, and tourn scoring data
 
    """

  
    if len(scoring_base) == 0:
        
        rd_1_data, rd_1_data_pts = missing_round("round_1")
        
        rd_2_data, rd_2_data_pts = missing_round("round_2")

        rd_3_data, rd_3_data_pts = missing_round("round_3")
        
        rd_4_data, rd_4_data_pts = missing_round("round_4")

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}

        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 1:
        
        round_1 = find_rd_number(scoring_base[0])
        m_rd1, m_rd2, m_rd3 = missing_round_number(scoring_base)

        

        rd_1 = scoring_base[0]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)

        rd_2_data, rd_2_data_pts = missing_round(m_rd1)
        rd_3_data, rd_3_data_pts = missing_round(m_rd2)
        rd_4_data, rd_4_data_pts = missing_round(m_rd3)
        

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}

        
        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 2:
        # missed cut

        round_1 = find_rd_number(scoring_base[1])
        round_2 = find_rd_number(scoring_base[0])

        m_rd1, m_rd2 = missing_round_number(scoring_base)
        

        rd_1 = scoring_base[1]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)
        
        rd_2 = scoring_base[0]
        rd_2_data, rd_2_data_pts = round_data(rd_2, round_2)

        rd_3_data, rd_3_data_pts = missing_round(m_rd1)
        rd_4_data, rd_4_data_pts = missing_round(m_rd2)

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}
        
        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 3:

        m_rd = missing_round_number(scoring_base)

        round_1 = find_rd_number(scoring_base[2])
        round_2 = find_rd_number(scoring_base[1])
        round_3 = find_rd_number(scoring_base[0])


        rd_1 = scoring_base[2]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)

        rd_2 = scoring_base[1]
        rd_2_data, rd_2_data_pts = round_data(rd_2, round_2)

        rd_3 = scoring_base[0]
        rd_3_data, rd_3_data_pts = round_data(rd_3, round_3)

        rd_4_data, rd_4_data_pts = missing_round(m_rd)

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}

        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 4:
        
        round_1 = find_rd_number(scoring_base[3])
        round_2 = find_rd_number(scoring_base[2])
        round_3 = find_rd_number(scoring_base[1])
        round_4 = find_rd_number(scoring_base[0])

        rd_1 = scoring_base[3]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)
        
        rd_2 = scoring_base[2]
        rd_2_data, rd_2_data_pts = round_data(rd_2, round_2)

        rd_3 = scoring_base[1]
        rd_3_data, rd_3_data_pts = round_data(rd_3, round_3)

        rd_4 = scoring_base[0]
        rd_4_data, rd_4_data_pts = round_data(rd_4, round_4)

        

        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}
        
        assert len(rds_data) == 144
        return rds_data

    elif len(scoring_base) == 5:
        # playoff round
        round_1 = find_rd_number(scoring_base[4])
        round_2 = find_rd_number(scoring_base[3])
        round_3 = find_rd_number(scoring_base[2])
        round_4 = find_rd_number(scoring_base[1])
        
        rd_1 = scoring_base[4]
        rd_1_data, rd_1_data_pts = round_data(rd_1, round_1)
        
        rd_2 = scoring_base[3]
        rd_2_data, rd_2_data_pts = round_data(rd_2, round_2)

        
        rd_3 = scoring_base[2]
        rd_3_data, rd_3_data_pts = round_data(rd_3, round_3)

        rd_4 = scoring_base[1]
        rd_4_data, rd_4_data_pts = round_data(rd_4, round_4)


        rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                    **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}
        
        
        assert len(rds_data) == 144
        return rds_data

    else:
        print(len(scoring_base), " incorrect number of rounds\n")

def handle_bad_page(player_info):
    """Handle page errors
    
    Args:
        player_info (dict) : player information

        player_scores (dict) : player scoring data

    Returns:
        Updated player data to handle espn server error
    """
    new_player_info = player_info

    
    if new_player_info["player_id"] == "4686087" and new_player_info["tournament_id"] == "401155472":

        new_shot_scores = {"round_1_1": 4,
                        "round_1_2": 5,
                        "round_1_3": 5,
                        "round_1_4": 4,
                        "round_1_5": 5,
                        "round_1_6": 7,
                        "round_1_7": 4,
                        "round_1_8": 4,
                        "round_1_9": 4,
                        "round_1_10": 4,
                        "round_1_11": 4,
                        "round_1_12": 4,
                        "round_1_13": 3,
                        "round_1_14": 4,
                        "round_1_15": 4,
                        "round_1_16": 4,
                        "round_1_17": 3,
                        "round_1_18": 6,
                        
                        "round_2_1": 4,
                        "round_2_2": 4,
                        "round_2_3": 3,
                        "round_2_4": 4,
                        "round_2_5": 4,
                        "round_2_6": 4,
                        "round_2_7": 4,
                        "round_2_8": 3,
                        "round_2_9": 5,
                        "round_2_10": 4,
                        "round_2_11": 4,
                        "round_2_12": 5,
                        "round_2_13": 5,
                        "round_2_14": 5,
                        "round_2_15": 3,
                        "round_2_16": 3,
                        "round_2_17": 3,
                        "round_2_18": 4,
                        
                        "round_3_1": None,
                        "round_3_2": None,
                        "round_3_3": None,
                        "round_3_4": None,
                        "round_3_5": None,
                        "round_3_6": None,
                        "round_3_7": None,
                        "round_3_8": None,
                        "round_3_9": None,
                        "round_3_10": None,
                        "round_3_11": None,
                        "round_3_12": None,
                        "round_3_13": None,
                        "round_3_14": None,
                        "round_3_15": None,
                        "round_3_16": None,
                        "round_3_17": None,
                        "round_3_18": None,
                        
                        "round_4_1": None,
                        "round_4_2": None,
                        "round_4_3": None,
                        "round_4_4": None,
                        "round_4_5": None,
                        "round_4_6": None,
                        "round_4_7": None,
                        "round_4_8": None,
                        "round_4_9": None,
                        "round_4_10": None,
                        "round_4_11": None,
                        "round_4_12": None,
                        "round_4_13": None,
                        "round_4_14": None,
                        "round_4_15": None,
                        "round_4_16": None,
                        "round_4_17": None,
                        "round_4_18": None,}

        new_hole_scores = {"round_1_1_pts": "par",
                        "round_1_2_pts": "bogey",
                        "round_1_3_pts": "bogey",
                        "round_1_4_pts": "bogey",
                        "round_1_5_pts": "bogey",
                        "round_1_6_pts": "double",
                        "round_1_7_pts": "par",
                        "round_1_8_pts": "bogey",
                        "round_1_9_pts": "par",
                        "round_1_10_pts": "par",
                        "round_1_11_pts": "par",
                        "round_1_12_pts": "birdie",
                        "round_1_13_pts": "par",
                        "round_1_14_pts": "par",
                        "round_1_15_pts": "par",
                        "round_1_16_pts": "par",
                        "round_1_17_pts": "par",
                        "round_1_18_pts": "bogey",
                        
                        "round_2_1_pts": "par",
                        "round_2_2_pts": "par",
                        "round_2_3_pts": "birdie",
                        "round_2_4_pts": "bogey",
                        "round_2_5_pts": "par",
                        "round_2_6_pts": "birdie",
                        "round_2_7_pts": "par",
                        "round_2_8_pts": "par",
                        "round_2_9_pts": "bogey",
                        "round_2_10_pts": "par",
                        "round_2_11_pts": "par",
                        "round_2_12_pts": "par",
                        "round_2_13_pts": "double",
                        "round_2_14_pts": "bogey",
                        "round_2_15_pts": "birdie",
                        "round_2_16_pts": "birdie",
                        "round_2_17_pts": "par",
                        "round_2_18_pts": "birdie",
                        
                        "round_3_1_pts": None,
                        "round_3_2_pts": None,
                        "round_3_3_pts": None,
                        "round_3_4_pts": None,
                        "round_3_5_pts": None,
                        "round_3_6_pts": None,
                        "round_3_7_pts": None,
                        "round_3_8_pts": None,
                        "round_3_9_pts": None,
                        "round_3_10_pts": None,
                        "round_3_11_pts": None,
                        "round_3_12_pts": None,
                        "round_3_13_pts": None,
                        "round_3_14_pts": None,
                        "round_3_15_pts": None,
                        "round_3_16_pts": None,
                        "round_3_17_pts": None,
                        "round_3_18_pts": None,
                        
                        "round_4_1_pts": None,
                        "round_4_2_pts": None,
                        "round_4_3_pts": None,
                        "round_4_4_pts": None,
                        "round_4_5_pts": None,
                        "round_4_6_pts": None,
                        "round_4_7_pts": None,
                        "round_4_8_pts": None,
                        "round_4_9_pts": None,
                        "round_4_10_pts": None,
                        "round_4_11_pts": None,
                        "round_4_12_pts": None,
                        "round_4_13_pts": None,
                        "round_4_14_pts": None,
                        "round_4_15_pts": None,
                        "round_4_16_pts": None,
                        "round_4_17_pts": None,
                        "round_4_18_pts": None,}

        new_player_scores = {**new_shot_scores, **new_hole_scores}

    if new_player_info["player_id"] == "4686086" and new_player_info["tournament_id"] == "401155472":
        new_shot_scores = {"round_1_1": 4,
                        "round_1_2": 3,
                        "round_1_3": 3,
                        "round_1_4": 2,
                        "round_1_5": 4,
                        "round_1_6": 5,
                        "round_1_7": 4,
                        "round_1_8": 2,
                        "round_1_9": 5,
                        "round_1_10": 4,
                        "round_1_11": 5,
                        "round_1_12": 5,
                        "round_1_13": 3,
                        "round_1_14": 4,
                        "round_1_15": 4,
                        "round_1_16": 4,
                        "round_1_17": 3,
                        "round_1_18": 5,
                        
                        "round_2_1": 4,
                        "round_2_2": 4,
                        "round_2_3": 4,
                        "round_2_4": 3,
                        "round_2_5": 4,
                        "round_2_6": 5,
                        "round_2_7": 4,
                        "round_2_8": 3,
                        "round_2_9": 4,
                        "round_2_10": 5,
                        "round_2_11": 5,
                        "round_2_12": 5,
                        "round_2_13": 3,
                        "round_2_14": 4,
                        "round_2_15": 4,
                        "round_2_16": 4,
                        "round_2_17": 3,
                        "round_2_18": 6,
                        
                        "round_3_1": None,
                        "round_3_2": None,
                        "round_3_3": None,
                        "round_3_4": None,
                        "round_3_5": None,
                        "round_3_6": None,
                        "round_3_7": None,
                        "round_3_8": None,
                        "round_3_9": None,
                        "round_3_10": None,
                        "round_3_11": None,
                        "round_3_12": None,
                        "round_3_13": None,
                        "round_3_14": None,
                        "round_3_15": None,
                        "round_3_16": None,
                        "round_3_17": None,
                        "round_3_18": None,
                        
                        "round_4_1": None,
                        "round_4_2": None,
                        "round_4_3": None,
                        "round_4_4": None,
                        "round_4_5": None,
                        "round_4_6": None,
                        "round_4_7": None,
                        "round_4_8": None,
                        "round_4_9": None,
                        "round_4_10": None,
                        "round_4_11": None,
                        "round_4_12": None,
                        "round_4_13": None,
                        "round_4_14": None,
                        "round_4_15": None,
                        "round_4_16": None,
                        "round_4_17": None,
                        "round_4_18": None,}

        new_hole_scores = {"round_1_1_pts": "par",
                        "round_1_2_pts": "par",
                        "round_1_3_pts": "par",
                        "round_1_4_pts": "par",
                        "round_1_5_pts": "par",
                        "round_1_6_pts": "par",
                        "round_1_7_pts": "par",
                        "round_1_8_pts": "par",
                        "round_1_9_pts": "par",
                        "round_1_10_pts": "bogey",
                        "round_1_11_pts": "bogey",
                        "round_1_12_pts": "par",
                        "round_1_13_pts": "par",
                        "round_1_14_pts": "par",
                        "round_1_15_pts": "par",
                        "round_1_16_pts": "par",
                        "round_1_17_pts": "par",
                        "round_1_18_pts": "bogey",
                        
                        "round_2_1_pts": "par",
                        "round_2_2_pts": "birdie",
                        "round_2_3_pts": "birdie",
                        "round_2_4_pts": "birdie",
                        "round_2_5_pts": "par",
                        "round_2_6_pts": "par",
                        "round_2_7_pts": "par",
                        "round_2_8_pts": "birdie",
                        "round_2_9_pts": "bogey",
                        "round_2_10_pts": "par",
                        "round_2_11_pts": "bogey",
                        "round_2_12_pts": "par",
                        "round_2_13_pts": "par",
                        "round_2_14_pts": "par",
                        "round_2_15_pts": "par",
                        "round_2_16_pts": "par",
                        "round_2_17_pts": "par",
                        "round_2_18_pts": "par",
                        
                        "round_3_1_pts": None,
                        "round_3_2_pts": None,
                        "round_3_3_pts": None,
                        "round_3_4_pts": None,
                        "round_3_5_pts": None,
                        "round_3_6_pts": None,
                        "round_3_7_pts": None,
                        "round_3_8_pts": None,
                        "round_3_9_pts": None,
                        "round_3_10_pts": None,
                        "round_3_11_pts": None,
                        "round_3_12_pts": None,
                        "round_3_13_pts": None,
                        "round_3_14_pts": None,
                        "round_3_15_pts": None,
                        "round_3_16_pts": None,
                        "round_3_17_pts": None,
                        "round_3_18_pts": None,
                        
                        "round_4_1_pts": None,
                        "round_4_2_pts": None,
                        "round_4_3_pts": None,
                        "round_4_4_pts": None,
                        "round_4_5_pts": None,
                        "round_4_6_pts": None,
                        "round_4_7_pts": None,
                        "round_4_8_pts": None,
                        "round_4_9_pts": None,
                        "round_4_10_pts": None,
                        "round_4_11_pts": None,
                        "round_4_12_pts": None,
                        "round_4_13_pts": None,
                        "round_4_14_pts": None,
                        "round_4_15_pts": None,
                        "round_4_16_pts": None,
                        "round_4_17_pts": None,
                        "round_4_18_pts": None,}


        new_player_scores = {**new_shot_scores, **new_hole_scores}

    new_player_data = {**new_player_info, **new_player_scores}
    
    return new_player_data


def player_scorecard(scorecard_url):
    """Get espn player scorecard for a specific tournament.

    Args:
        scorecard_url (str) : espn url
    
    Returns:
        player scoring data for tournament

    """
    with requests.Session() as session:
            
        page = session.get(scorecard_url)

        if page.status_code == 200:

            soup = BeautifulSoup(page.content, "lxml")
            base = soup.find_all("div", class_="roundSwap active")
            
            if base is not None:
                id_data = {}

                p_id_start = scorecard_url.find("id") + 3
                p_id_end = scorecard_url.rfind("tournamentId") - 1

                id_data["player_id"] = scorecard_url[p_id_start:p_id_end]
                id_data["tournament_id"] = scorecard_url[scorecard_url.rfind("/") + 1:]

                scorecard_data = scoring_data(base)
                player_data = {**id_data, **scorecard_data}

                assert len(player_data) == 146
                
                return player_data
        else:
            id_data = {}

            p_id_start = scorecard_url.find("id") + 3
            p_id_end = scorecard_url.rfind("tournamentId") - 1

            id_data["player_id"] = scorecard_url[p_id_start:p_id_end]
            id_data["tournament_id"] = scorecard_url[scorecard_url.rfind("/") + 1:]

            scorecard_data = {}

            if id_data["player_id"] == "4686086" and id_data["tournament_id"] == "401155472":
                scorecard_data = handle_bad_page(id_data)

            if id_data["player_id"] == "4686087" and id_data["tournament_id"] == "401155472":
                scorecard_data = handle_bad_page(id_data)


            if scorecard_data:

                player_data = {**id_data, **scorecard_data}
            else:
                rd_1_data, rd_1_data_pts = missing_round("round_1")
        
                rd_2_data, rd_2_data_pts = missing_round("round_2")

                rd_3_data, rd_3_data_pts = missing_round("round_3")
                
                rd_4_data, rd_4_data_pts = missing_round("round_4")

                rds_data = {**rd_1_data, **rd_2_data, **rd_3_data, **rd_4_data,
                            **rd_1_data_pts, **rd_2_data_pts, **rd_3_data_pts, **rd_4_data_pts}

                assert len(rds_data) == 144

                player_data = {**id_data, **rds_data}

            assert len(player_data) == 146
                
            return player_data
            

def players_scorecard_from_tournament(url):
    """Finds all participants in tournament and gets tournament scorecard data for each player

    Args:
        url (str) : espn tournament

    Returns:
        player data from tournament
    """
    espn_home_url = "https://www.espn.com/golf/"

    t_id = url[url.rfind("=")+1:]
    base_url = url

    # Redirect server request to mimic more realistic behavior
    # h_page = requests.get(espn_home_url)
    if (t_id != "1155") and (t_id != "995"):

        with requests.Session() as session:

            time.sleep(3)
            
            # home_page = session.get(espn_home_url)

            page = session.get(base_url)

            if page.status_code == 200: 
                print("good url: ", url)
            
                soup = BeautifulSoup(page.content, "lxml")
                # Table's on webpage. index with -1 in case of playoff table
                tourn_tables = soup.select("div.ResponsiveTable")

                if tourn_tables is not None:

                    if len(tourn_tables) == 1:
                        
                        tourn_table = tourn_tables[-1]
                        tourn_body = tourn_table.find("tbody", class_="Table__TBODY")

                        tourn_players = get_player_ids(tourn_body)
                        # 'https://www.espn.com/golf/player/scorecards/_/id/11099tournamentId/401148233'
                        scorecard_front = "https://www.espn.com/golf/player/scorecards/_/id/"
                        scorecard_back = "/tournamentId/"
                        valid_player_urls = [scorecard_front + player + scorecard_back + t_id 
                                            for player in tourn_players]

                        # print(valid_player_urls)
                        player_data = [player_scorecard(player) for player in valid_player_urls]
                        print("\nNumber of players: ", len(player_data))
                        return player_data

                    elif len(tourn_tables) == 2:

                        tourn_table = tourn_tables[-1]
                        tourn_body = tourn_table.find("tbody", class_="Table__TBODY")

                        tourn_players = get_player_ids(tourn_body)
                        # 'https://www.espn.com/golf/player/scorecards/_/id/11099tournamentId/401148233'
                        scorecard_front = "https://www.espn.com/golf/player/scorecards/_/id/"
                        scorecard_back = "/tournamentId/"
                        valid_player_urls = [scorecard_front + player + scorecard_back + t_id 
                                            for player in tourn_players]

                        # print(valid_player_urls)
                        player_data = [player_scorecard(player) for player in valid_player_urls]
                        print("\nNumber of players: ", len(player_data))
                        return player_data

                    elif len(tourn_tables) == 0:
                        
                        print(f"error with {url}")
                        # To reset error on espn server
                        page = session.get(espn_home_url)
                        return url
                        # return None

                    else:
                        print(f"Number of tables {len(tourn_tables)} in url {url}")

            else:
                h_page = session.get(espn_home_url)

                # return None
    

def write_tournament_data(tournament_url, h_data_path="base"):
    """Write historical tournament data to disk

    Args:
        tournament_url (str) : espn tournament

    """
    # Get data for file
    tourn_data = players_scorecard_from_tournament(tournament_url)

    # Create columns for csv file
    tournament_ids = ["player_id", "tournament_id"]
    rd_nums = ["1_", "2_", "3_", "4_"]
    rd_ids = ["round_" + rd_num + str(i) for rd_num in rd_nums for i in range(1,19)]
    rd_pt_ids = [ids + "_pts" for ids in rd_ids]

    tournament_ids.extend(rd_ids)
    tournament_ids.extend(rd_pt_ids)

    fields = tournament_ids

    # Create unique file path from tournament id
    t_id = tournament_url[tournament_url.rfind("=")+1:]
    fn = t_id + ".csv"
    # Changed f_path for testing purpose and to not mix with already correct historical data
    # When ready change path back to config.RAW_HISTORICAL_DIR
    if h_data_path == "base":
        f_path = str(Path(config.RAW_HISTORICAL_DIR, fn))
    
    elif h_data_path == "pga_season_2011":
        f_path = str(Path(config.PGA_SEASON_2011, fn))

    elif h_data_path == "pga_season_2012":
        f_path = str(Path(config.PGA_SEASON_2012, fn))

    elif h_data_path == "pga_season_2013":
        f_path = str(Path(config.PGA_SEASON_2013, fn))

    elif h_data_path == "pga_season_2014":
        f_path = str(Path(config.PGA_SEASON_2014, fn))

    elif h_data_path == "pga_season_2015":
        f_path = str(Path(config.PGA_SEASON_2015, fn))

    elif h_data_path == "pga_season_2016":
        f_path = str(Path(config.PGA_SEASON_2016, fn))

    else:
        print(f"No directory called {h_data_path}. Used historical_player_data directory")
        f_path = str(Path(config.RAW_HISTORICAL_DIR, fn))
    # fn = f_path + t_id + ".csv"

    with open (f_path, "w", newline="") as csvfile:
        writer = DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
         
        if tourn_data is not None:

            writer.writerows(tourn_data)
        else:
            print(f"The tourn data is None: {tourn_data}")
    

    msg = f"Finished {t_id}"
    return msg


def csv_tournament_data(tournament_urls):
    """Write all tournament data using csv file format.

    Args:
        tournament_urls (list) : espn tournaments

    """
    futures_list = []
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for url in tournament_urls:
            futures = executor.submit(write_tournament_data, url)
            futures_list.append(futures)

        for future in futures_list:
            try:
                result = future.result(timeout=300)
                results.append(result)
            except Exception as exc:
                # print(f"{result} generated an excpetion {exc}")
                results.append(None)
        return results

def p_csv_tournament_data(tournament_urls, f_path="base"):
    """Write all tournament data using csv file format.
    
    Args:
        tournament_urls (list) : espn tournaments

    """

    futures_list = []
    results = []
    with ProcessPoolExecutor(max_workers=8) as executor:
        for url in tournament_urls:
            futures = executor.submit(write_tournament_data, url, f_path)
            futures_list.append(futures)

        for future in futures_list:
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                # print(f"{result} generated an excpetion {exc}")
                results.append(None)
        return results


@timeit
def historical_data_runner(start, end=None, f_path=None):
    """Get historical data over given pga season(s)
    
    Args:
        start (int) : beginning pga season

        end (int) : ending pga season, optional arg

        f_path (str) : historical data directory to store data

    Returns:
        missed tournaments from to many server requests and failed connections
    """
    if end is not None:

        tournaments_df = get_espn_tournaments(start, end)
    else:
        tournaments_df = get_espn_tournaments(start)

    print(f"Number of tournaments: {tournaments_df.shape[0]}")

    base_url = "https://www.espn.com/golf/leaderboard?tournamentId="

    tournaments_df["url"] = tournaments_df["tournament_id"].apply(lambda x: base_url + str(x))

    urls = tournaments_df["url"].tolist()

    if f_path is not None:
    
        results = p_csv_tournament_data(urls, f_path)
    
    else:
        results = p_csv_tournament_data(urls)
    
    missed_tourns = []
    tourn_counter = 0
    for result in results:
        if result is None:
            missed_tourns.append(urls[tourn_counter])
            print(f"URL:{urls[tourn_counter]} TYPE: {(type(urls[tourn_counter]))}")
            print(f"Length of URL : {len(urls[tourn_counter])}")
        else:
            print(result)
        tourn_counter += 1

    return missed_tourns
    # missed_results = [write_tournament_data(url) for url in missed_tourns]
    



def st_historical_data_runner(start, end=None):
    """Get historical data over given pga season(s) from espn through
    a single thread process.

    Note:
    Process writes each tournament to disk as a csv file using the
    tournament id as a unique identifier.
    
    Args:
        start (int) : beginning pga season

        end (int) : ending pga season, optional arg
    
    """
    if end is not None:

        tournaments_df = get_espn_tournaments(start, end)

    else:

        tournaments_df = get_espn_tournaments(start)


    base_url = "https://www.espn.com/golf/leaderboard?tournamentId="

    tournaments_df["url"] = tournaments_df["tournament_id"].apply(lambda x: base_url + str(x))

    urls = tournaments_df["url"].tolist()

    results = [write_tournament_data(url) for url in urls]
    
    print(results)

def tournament_date_col(df, tournament_df):
    """Create date column through tournament id mapping

    Parameters:
        df (pd.Dataframe)
        tournament_df (pd.Dataframe)
    """
    date_col = df["tournament_id"].apply(lambda x: tournament_df["date"][tournament_df["tournament_id"] == x].values[0])

    idx = 2
    df.insert(loc=idx, column="date", value=date_col)

def combine_files(root, pattern=None):
    """Combine all files in root path directory

    Parameters:
        root (str) : file path to directory of files
        pattern (str) : optional file pattern to search for in directory

    Returns:
        combined files
    """
    if pattern is not None:
        files = [PurePath(path, name) for path, subdirs, files in os.walk(root) for name in files if fnmatch(name, pattern)]
        combined_files = pd.concat([pd.read_csv(f) for f in files])

    else:
        files = [PurePath(path, name) for path, subdirs, files in os.walk(root) for name in files]
        combined_files = pd.concat([pd.read_csv(f) for f in files])

    run_date_transformation(combined_files)

    return combined_files.sort_values(by="date")

def merge_tournaments(f_pattern, f_name, f_path="raw_historical"):
    """Merge espn tournmants
    
    Args:
        f_pattern (str) : pattern criteria to match for files
        
        f_name (str) : file name for merged tournaments
        
    """
    file_p_dict = {"raw_historical": str(config.RAW_HISTORICAL),
                "seasons_2011_2016": str(config.PGA_SEASON_2011_2016),
                "raw_historical_dir": str(config.RAW_HISTORICAL_DIR)}
    full_path = file_p_dict[f_path]
    
    historical_data = combine_files(full_path, f_pattern)
    
    w_f_path = str(Path(config.PROCESSED_HISTORICAL, f_name))
    if os.path.isfile(w_f_path):
        # file exists so no need for headers
        historical_data.to_csv(w_f_path, mode="a", header=False, index=False, date_format="%Y-%m-%d")
    else:
        historical_data.to_csv(w_f_path, mode="a", header=True, index=False, date_format="%Y-%m-%d")


def run_date_transformation(df):
    """Run and save date transformations for historical player data
    
    Args:
        df (pd.DataFrame) : historical player data
    """
    # f_path = str(Path(config.PROCESSED_HISTORICAL_DIR, "hpd_2017_2020.csv"))
    # historical_data_df = pd.read_csv(f_path)

    espn_tourn_path = str(Path(config.RAW_DATA_DIR, "espn_tournaments_2011_2016.csv"))
    espn_tourns_df = pd.read_csv(espn_tourn_path, parse_dates=["date"])

    tournament_date_col(df, espn_tourns_df)

    # historical_data_df.to_csv(f_path)


if __name__ == "__main__":

    # tourn_errors = historical_data_runner(2011, f_path="pga_season_2011")

    # if tourn_errors:
    #     for tourn in tourn_errors:
    #         missed_result = write_tournament_data(tourn, "pga_season_2011")
    #         print(missed_result)
    

    merge_tournaments("*.csv", "hpd.csv")


    
    


    
        