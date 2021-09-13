from pathlib import Path
import sys
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config

import pandas as pd
import numpy as np

def tournament_position_rank(df):
    """Final position placing for tournament participants
    
    Args:
        df (pd.Dataframe) : historical player data

    """
    # Create indicator variablet
    df["make_cut"] = (df["round_3_18"] > 0) & (df["round_4_18"] > 0)
    # Check columns
    if df.columns[3] == "round_1_1" and df.columns[74] == "round_4_18":
        # select scoring columns to sum
        score_cols = df.columns[3:75].tolist()
        df["total"] = np.where(df.make_cut, df[score_cols].sum(axis=1), np.nan)
        df["place"] = df.groupby("tournament_id")["total"].rank("min")
    else:
        print("Incorrect columns for start and end of dataframe.\n")

def handle_placing_ties(df):
    """Handle position ties for winners of tournaments

    Args:
        df (pd.Dataframe) : historical player data

    """
    winners = df[df["place"] == 1].copy()
    df_ties = winners[winners["tournament_id"].duplicated(keep=False)]
    df_ties.reset_index(inplace=True)

    playoff_winners = df_ties.groupby("tournament_id").first()
    new_totals = playoff_winners[["index", "total"]].reset_index(drop=True)

    df["total"].iloc[new_totals["index"].values] = df["total"].iloc[new_totals["index"].values].apply(lambda x: x-1) 
    # Redo place col
    df["place"] = df.groupby("tournament_id")["total"].rank("min")


def place_pts():
    """Points given  to tournament participants for finishing position 

    """
    place_dict = {}
    for place in range(1,51):
        if place == 1:
            place_dict[place] = 30
        elif place == 2:
            place_dict[place] = 20
        elif place == 3:
            place_dict[place] = 18
        elif place == 4:
            place_dict[place] = 16
        elif place == 5:
            place_dict[place] = 14
        elif place == 6:
            place_dict[place] = 12
        elif place == 7:
            place_dict[place] = 10
        elif place == 8:
            place_dict[place] = 9
        elif place == 9:
            place_dict[place] = 8
        elif place == 10:
            place_dict[place] = 7
        elif place > 10 and place <= 15:
            place_dict[place] = 6
        elif place > 15 and place <= 20:
            place_dict[place] = 5
        elif place > 20 and place <= 25:
            place_dict[place] = 4
        elif place > 25 and place <= 30:
            place_dict[place] = 3
        elif place > 30 and place <= 40:
            place_dict[place] = 2
        elif place > 40 and place <= 50:
            place_dict[place] = 1
        else:
            continue

    place_df = pd.DataFrame(list(place_dict.items()), columns=["place", "place_pts"])
    return place_df


def map_placings(player_df, place_df):
    """Map position placings, for players, with placing points

    Args:
        player_df (pd.Dataframe) : historical player data
        place_df (pd.Dataframe) : draftkings fantasy position point totals
    """
    placing_conditions = [
        player_df["place"] == place_df["place"][0],
        player_df["place"] == place_df["place"][1],
        player_df["place"] == place_df["place"][2],
        player_df["place"] == place_df["place"][3],
        player_df["place"] == place_df["place"][4],
        player_df["place"] == place_df["place"][5],
        player_df["place"] == place_df["place"][6],
        player_df["place"] == place_df["place"][7],
        player_df["place"] == place_df["place"][8],
        player_df["place"] == place_df["place"][9],
        player_df["place"] == place_df["place"][10],
        player_df["place"] == place_df["place"][11],
        player_df["place"] == place_df["place"][12],
        player_df["place"] == place_df["place"][13],
        player_df["place"] == place_df["place"][14],
        player_df["place"] == place_df["place"][15],
        player_df["place"] == place_df["place"][16],
        player_df["place"] == place_df["place"][17],
        player_df["place"] == place_df["place"][18],
        player_df["place"] == place_df["place"][19],
        player_df["place"] == place_df["place"][20],
        player_df["place"] == place_df["place"][21],
        player_df["place"] == place_df["place"][22],
        player_df["place"] == place_df["place"][23],
        player_df["place"] == place_df["place"][24],
        player_df["place"] == place_df["place"][25],
        player_df["place"] == place_df["place"][26],
        player_df["place"] == place_df["place"][27],
        player_df["place"] == place_df["place"][28],
        player_df["place"] == place_df["place"][29],
        player_df["place"] == place_df["place"][30],
        player_df["place"] == place_df["place"][31],
        player_df["place"] == place_df["place"][32],
        player_df["place"] == place_df["place"][33],
        player_df["place"] == place_df["place"][34],
        player_df["place"] == place_df["place"][35],
        player_df["place"] == place_df["place"][36],
        player_df["place"] == place_df["place"][37],
        player_df["place"] == place_df["place"][38],
        player_df["place"] == place_df["place"][39],
        player_df["place"] == place_df["place"][40],
        player_df["place"] == place_df["place"][41],
        player_df["place"] == place_df["place"][42],
        player_df["place"] == place_df["place"][43],
        player_df["place"] == place_df["place"][44],
        player_df["place"] == place_df["place"][45],
        player_df["place"] == place_df["place"][46],
        player_df["place"] == place_df["place"][47],
        player_df["place"] == place_df["place"][48],
        player_df["place"] == place_df["place"][49],
        ]
    player_df["fantasy_placing_pts"] = np.select(placing_conditions, place_df["place_pts"])

def make_72_cols(base_col):
    """Make columns for holes in pga tournament

    Args:
        base_col (str) : base name for column

    Returns:
        columns for 72 holes
    """
    cols = []
    for rd in range(1,5):
        rd_base = base_col + str(rd)
        for hole in range(1,19):
            rd_h_cols = rd_base + "_" + str(hole)
            cols.append(rd_h_cols)
    return cols

def fantasy_hole_points(player_df):
    """Fantasy hole point mappings for player hole scores

    Args:
        player_df (pd.Dataframe) : historical player data

    """

    hole_fantasy_pts = {"eagle": 8, "birdie": 3,"par": 0.5, "bogie": -0.5, "double": -1}
    fantasy_pts_df = pd.DataFrame(list(hole_fantasy_pts.items()), columns=["hole_score", "points"])

    fantasy_points_conditions = [
        player_df.loc[:, "round_1_1_pts":"round_4_18_pts"] == fantasy_pts_df.iloc[0,0],
        player_df.loc[:, "round_1_1_pts":"round_4_18_pts"] == fantasy_pts_df.iloc[1,0],
        player_df.loc[:, "round_1_1_pts":"round_4_18_pts"] == fantasy_pts_df.iloc[2,0],
        player_df.loc[:, "round_1_1_pts":"round_4_18_pts"] == fantasy_pts_df.iloc[3,0],
        player_df.loc[:, "round_1_1_pts":"round_4_18_pts"] == fantasy_pts_df.iloc[4,0]
    ]
    f_cols = make_72_cols("f_pts_")
    player_df[f_cols] = np.select(fantasy_points_conditions, fantasy_pts_df["points"])
    player_df["fantasy_hole_score_pts"] = player_df[f_cols].sum(axis=1)

def finished_rounds(player_df):
    """Makes columns to identify which players completed each round (i.e. all 18 holes)
    
    Args:
        player_df (pd.Dataframe) : historical player data
    """
    player_df["complete_r1"] = player_df.round_1_18 > 0
    player_df["complete_r2"] = player_df.round_2_18 > 0
    player_df["complete_r3"] = player_df.round_3_18 > 0
    player_df["complete_r4"] = player_df.round_4_18 > 0

def bogey_free_rounds(player_df):
    """Create bogey free round fantasy point column
    
    Note: Add 3 points per bogey free round in tournament
    
    Args:
        player_df (pd.Dataframe) : historical player data

    """
    # Filter for rd1, rd2, rd3, and rd4 columns
    fant1_cols = [col for col in player_df.columns.tolist() if col.find("f_pts_1_") != -1]
    fant2_cols = [col for col in player_df.columns.tolist() if col.find("f_pts_2_") != -1]
    fant3_cols = [col for col in player_df.columns.tolist() if col.find("f_pts_3_") != -1]
    fant4_cols = [col for col in player_df.columns.tolist() if col.find("f_pts_4_") != -1]
    # fantasy hole points lower than 0 is a result of a score of boegy or worse
    b_rd1 = player_df[fant1_cols] < 0
    b_rd2 = player_df[fant2_cols] < 0
    b_rd3 = player_df[fant3_cols] < 0
    b_rd4 = player_df[fant4_cols] < 0

    # Add together True's. So if the resulting number is greater than 0 the player had a bogey in his round
    player_df["bf1"] = np.where(player_df.complete_r1, b_rd1.sum(axis=1), np.nan)
    player_df["bf2"] = np.where(player_df.complete_r2, b_rd2.sum(axis=1), np.nan)
    player_df["bf3"] = np.where(player_df.complete_r3, b_rd3.sum(axis=1), np.nan)
    player_df["bf4"] = np.where(player_df.complete_r4, b_rd4.sum(axis=1), np.nan)

    bf_cols = [col for col in player_df.columns.tolist() if col.find("bf") != -1]
    player_df["fantasy_bogeyfree_pts"] = (player_df[bf_cols] == 0).astype(int).sum(axis=1) * 3

def find_subsequence(seq, subseq):
    target = np.dot(subseq, subseq)
    candidates = np.where(np.correlate(seq,
                                       subseq, mode='valid') == target)[0]
    # some of the candidates entries may be false positives, double check
    check = candidates[:, np.newaxis] + np.arange(len(subseq))
    mask = np.all((np.take(seq, check) == subseq), axis=-1)
    # yield from candidates[mask] # (generator way)
    return candidates[mask]
    
def birdie_streak(df):
    """Find three consecutive birdies on player scorecard

    Args:
        df (pd.Dataframe) : historical player data

    """
    np_df = df.to_numpy()
    rc = 0
    b_seq = [3,3,3]
    birdie_steak = []
    for player in np_df:
        x = find_subsequence(player, b_seq)
        if x.size > 0:
            birdie_steak.append(3)
        else:
            birdie_steak.append(0)
    return birdie_steak

def make_birdie_streak(df):
    """Create biridie streak fantasy point columns

    Args:
        df (pd.Dataframe) : historical player data
    """
    f1_cols = [col for col in df.columns.tolist() if col.find("f_pts_1") != -1]
    f2_cols = [col for col in df.columns.tolist() if col.find("f_pts_2") != -1]
    f3_cols = [col for col in df.columns.tolist() if col.find("f_pts_3") != -1]
    f4_cols = [col for col in df.columns.tolist() if col.find("f_pts_4") != -1]

    b_f1 = birdie_streak(df[f1_cols])
    b_f2 = birdie_streak(df[f2_cols])
    b_f3 = birdie_streak(df[f3_cols])
    b_f4 = birdie_streak(df[f4_cols])

    df["birdie_streak_r1"] = b_f1
    df["birdie_streak_r2"] = b_f2
    df["birdie_streak_r3"] = b_f3
    df["birdie_streak_r4"] = b_f4

    df["fantasy_birdie_streak_pts"] = df.loc[:, "birdie_streak_r1":"birdie_streak_r4"].sum(axis=1)

def hole_in_ones(df):
    """Create hole in one fantasy point column

    Notes:
        Gives 5 points per hole in one to player

    Args:
        df (pd.Dataframe)

    """
    rd_cols = df.columns.tolist()[3:75]
    df["fantasy_hole_in_one_pts"] = df[rd_cols].isin([1]).sum(axis=1) * 5

def under70(df):
    """Create under 70 fantasy point column

    Note:
        5 point fantasy bonus for player with all four completed (full 18 holes) rounds under 70

    Args:
        df (pd.Dataframe) : historical player data

    """
    rd1_cols = [col for col in df.columns.tolist() if col.find("rd_1") != -1]
    rd2_cols = [col for col in df.columns.tolist() if col.find("rd_2") != -1]
    rd3_cols = [col for col in df.columns.tolist() if col.find("rd_3") != -1]
    rd4_cols = [col for col in df.columns.tolist() if col.find("rd_4") != -1]

    df["rd_total_1"] = np.where(df.complete_r1, df[rd1_cols].sum(axis=1), np.nan)
    df["rd_total_2"] = np.where(df.complete_r2, df[rd2_cols].sum(axis=1), np.nan)
    df["rd_total_3"] = np.where(df.complete_r3, df[rd3_cols].sum(axis=1), np.nan)
    df["rd_total_4"] = np.where(df.complete_r4, df[rd4_cols].sum(axis=1), np.nan)

    total_1 = df["rd_total_1"] < 70
    total_2 = df["rd_total_2"] < 70
    total_3 = df["rd_total_3"] < 70
    total_4 = df["rd_total_4"] < 70

    df["under70_1"] = np.where(total_1, 1, 0)
    df["under70_2"] = np.where(total_2, 1, 0)
    df["under70_3"] = np.where(total_3, 1, 0)
    df["under70_4"] = np.where(total_4, 1, 0)

    under70_cols = [col for col in df.columns.tolist() if col.find("under70") != -1]
    df["fantasy_under70_pts"] = np.where(df[under70_cols].sum(axis=1) == 4, 5, 0)

def total_fantasy_points(df):
    """Calculate total fantasy points over course of tournament

    Args:
        df (pd.Dataframe) : historical player data
    """
    f_cols = [col for col in df.columns.tolist() if col.find("fantasy_") != -1]
    df["fantasy_total_points"] = df[f_cols].sum(axis=1)

def fantasy_map_runner():
    """Run draftkings fantansy transformation mappings
    """
    f_path = str(Path(config.PROCESSED_HISTORICAL_DIR, "hpd_2017_2020.csv"))
    dk_fantasy_path = str(Path(config.PROCESSED_HISTORICAL_DIR, "draftkings_hpd_2017_2020.csv"))
    historical_data_df = pd.read_csv(f_path, parse_dates=["date"])

    tournament_position_rank(historical_data_df)

    handle_placing_ties(historical_data_df)
    places_df = place_pts()

    map_placings(historical_data_df, places_df)
    fantasy_hole_points(historical_data_df)
    finished_rounds(historical_data_df)

    
    bogey_free_rounds(historical_data_df)
    make_birdie_streak(historical_data_df)
    hole_in_ones(historical_data_df)
    under70(historical_data_df)
    total_fantasy_points(historical_data_df)

    historical_data_df.to_csv(dk_fantasy_path, index=False)


if __name__ == "__main__":

    fantasy_map_runner()

    