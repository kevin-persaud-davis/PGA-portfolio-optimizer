from pathlib import Path
import sys
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\src\\data")

import config

import pandas as pd
import numpy as np


# First find the competitors in that week's tournament
# For demonstratitive purposes I will use one tournament and scale to more one
# I know the case of one tournament is done

# Information needed to identifiy competitors in current week's tournament

# tournament id of that week -> Find all player id's (competitors)

# Check that each player id is in the historical dataset. It may be the case that this
# tournament is a player's first tournament (for whatever reason) and it's easier if they
# are dropped from consideration

# Expected value/Mean vector
# For now the rolling 2 tournament average will be used
# In the future, a call to the trained model will be made and predictions 
# of players final total fantasy points will be sent/given

# Covariance/correlation matrix of player's historical realized performances
# Since each player does not have the same fequency of play, I must first
# calculate the std of each player. If the value for any player is NA, then drop the 
# player from the both datasets (historical and current week. Won't consider that player for optimizer)

# Pivot the dataframe so that each player has it's own column
# fillna with 0's and calculate the correlation matrix. Fill the diagonal with player's std
# Check that shape's match before inputing values

def check_competitors_historical(historical_player_df, current_df):
    """Check that each player competiting in this week's tournament
    has historical data to perform forecast estimates and codependence measures
    
    Args:
        historical_player_df (pd.DataFrame) : historical player id's

        current_df (pd.DataFrame) : current week tournament

    Returns:
        current week competitors with at least one instance of historical data
    """
    all_competitors = current_df.player_id.unique()

    historical_competitors_df = historical_player_df[historical_player_df["player_id"].isin(all_competitors)]

    # competitors_historical_df = historical_player_df[historical_df["player_id"].isin(all_competitors)]

    m_mask = np.isin(all_competitors, historical_competitors_df["player_id"].unique())
    remove_pids = all_competitors[~m_mask]

    remove_pid_idxs = current_df[current_df.player_id.isin(remove_pids)].index
    current_df = current_df.drop(index=remove_pid_idxs)

    this_week_competitors = current_df.player_id.unique()


    if np.array_equal(np.sort(historical_competitors_df.player_id.unique()), np.sort(this_week_competitors)):
        return this_week_competitors
    
    else:
        print("Competiting player error. Please check player list between two dataframes.")

def rolling_mean_score(scoring, days=2):
    """Compute rolling mean fantasy score over given number of days
    
    Args:
        scoring (pd.DataFrame) : DataFrame consisting of player_id and
                                fantasy_total_points
        
        days (int) : rolling period to be used
    
    Returns:
        rolling mean score over given days
    """
    scores = scoring.groupby("player_id")["fantasy_total_points"].rolling(days, min_periods=days).mean()
    scores = scores.reset_index().set_index("level_1").drop(columns="player_id")
    return scores

def get_tournament_competitors(current_df):
    """Get all players competiting in tournament
    
    Args:
        current_df (pd.DataFrame) : current week's tournament

    Returns:
        Players competiting in tournament
    """
    return current_df["player_id"].unique()


def main():
    

    feature_store_path = str(Path(config.TIMESERIES_FRAMEWORK_DIR, "ts_feature_store.csv"))
    feature_df = pd.read_csv(feature_store_path, parse_dates=["date"])

    # arbitrary selection of tournament to test. More robust functionality will be provided
    # after the implementation for one tournament is correct


    current_week_tournament = [401148239]
    # Split data between historical and upcoming tournament
    current_tourn_df = feature_df[feature_df["tournament_id"] == current_week_tournament[0]].copy()
    historical_df = feature_df[~(feature_df["tournament_id"] == current_week_tournament[0])].copy()


    # ML estimates will be used in the future instead of historical averages
    historical_df["expected_value"] = rolling_mean_score(historical_df[["player_id", "fantasy_total_points"]])

    current_competitors = check_competitors_historical(historical_df[["player_id"]], current_tourn_df)

    historical_estimate_cols = ["player_id", "tournament_id", "fantasy_total_points", "expected_value"]
    historical_competitors_df = historical_df[historical_estimate_cols][historical_df.player_id.isin(current_competitors)]

    competitors_std = historical_competitors_df[["player_id", "fantasy_total_points"]].groupby("player_id").agg(
        std = pd.NamedAgg(column="fantasy_total_points", aggfunc="std"),
    )

    input_matrix = historical_competitors_df[historical_estimate_cols[:-1]].pivot(index="tournament_id",
                                                                                columns="player_id", 
                                                                                values="fantasy_total_points").fillna(0)
    
    corr = input_matrix.corr()

    np.fill_diagonal(corr.values, competitors_std)

    # Now that all the competitors are valid, I can compute the std of each player before dropping rows to make 
    # dispersion measurement more robust (more data points)




if __name__ == "__main__":
    
    main()