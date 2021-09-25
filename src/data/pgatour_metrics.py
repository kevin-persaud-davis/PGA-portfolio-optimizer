from pathlib import Path
from unicodedata import normalize
import sys
from itertools import chain


sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config

import requests
from bs4 import BeautifulSoup
import pandas as pd


def pgatour_tournament_ids(url):
    """Find pgatour.com tournament ids on webpage

    Args:
        url (str) : pgatour.com stats webpage
    
    Returns:
        tournament_ids, with entires of (tournament_id, tournament_name)
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "lxml")

    season = int(url[url.rfind("y") + 1:url.rfind(".")])

    headers = soup.find("section", class_="statistics-details-content")
    tournaments_info = []
    
    if headers is not None:
        
        tournament_parent = headers.find_all("div", 
                                    class_="statistics-details-select-wrap tournament")
        if tournament_parent is not None:
            
            tournaments = tournament_parent[0].find_all("option")
            for tourn in tournaments:
                
                tournaments_info.append((tourn["value"], tourn.text, season))

    return tournaments_info

def get_pgatour_ids(start, end):
    """Get pgatour.com tournament ids for a range of seasons
    
    Args:
        start (int) : start season
        
        end (int): end season
    
    Returns:
        pgatour tournament ids
    """
    seasons = [year for year in range(start, end+1)]

    # same tournament id's for all stat pages on pgatour.com
    urls = [f"https://www.pgatour.com/content/pgatour/stats/stat.328.y{season}.html" 
            for season in seasons]

    pgatour_ids = [pgatour_tournament_ids(url) for url in urls]

    # flatten data
    pgatour_ids = list(chain.from_iterable(pgatour_ids))

    return pgatour_ids

def save_pgatour_ids(file_p):
    """Save pgatour tournament ids in given file path

    Args:
        file_p (str) : file path

    """
    pgatour_data = get_pgatour_ids(2017, 2020)

    df = pd.DataFrame(pgatour_data, columns=["tournament_id", "tournament_name", "season"])

    df.to_csv(file_p, index=False)

def get_espn_tournaments(start, end=None, all_tournaments=False):
    """Get espn tournaments for given season(s).

    Notes:
    if all_tournaments is left as False, the dataframe of tournaments
    will contain only valid tournamets. Otherwise tournaments that have
    not been cancelled will be given (this includes tournaments of match play,
    charity events, etc.)

    Args:
        start (int) : starting pga season
        end (int) : ending pga season, optional
        all_tournaments (bool) : get all or valid tournaments

    Returns:
        dataframe of tournaments for specified season(s)
    """
    if all_tournaments:
        pass
    else:
        # change path to point to 2011 to 2016 espn tournaments
        valid_tournaments_path = str(Path(config.TOURNAMENTS_DIR, "valid_espn_tournaments_2011_2016.csv"))
        df = pd.read_csv(valid_tournaments_path,  date_parser=["date"])

    if end is not None:
        season_df = df[(df.season_id >= start) & (df.season_id <= end)]

    else:
        season_df = df[df.season_id == start]

    return season_df


def pgatour_statistic(url):
    """Get data on give pgatour statistic

    Args:
        url (str) : pgatour statistic url

    Returns:
        data of pgatour statistic
    """
    with requests.Session() as session:
            
        page = session.get(url)

    
        soup = BeautifulSoup(page.content, "lxml")
        print(f"Fetching: {url}")
        
        data = []
        data_keys = []

        # meta-information
        pga_stat_id = url[url.rfind("stat.") + 5 : url.rfind(".y")]
        pga_tourn_id = url[url.rfind("off.") + 4 : url.rfind(".")]
        pga_season_id = url[url.rfind("y") + 1: url.rfind(".eoff")]

        statistic_name = soup.select("section.statistics-details-content")
        if statistic_name is not None:
            name_header = statistic_name[0].find("div", class_="header")
            name = name_header.find("h1")
            if name is not None:
                pga_stat_name = name.text
                pga_stat_name = pga_stat_name.replace(" ", "_")

        statistic_table = soup.select("div.details-table-wrap")
        if statistic_table is not None:
            header = statistic_table[0].find("thead")
            if header is not None:
                header_cols = header.find_all("th")
                for h_col in header_cols:
                    col_str = h_col.text
                    col_str = normalize('NFKD',col_str)
                    col_str = col_str.strip()
                    col_str = col_str.replace(" ", "_")
                    data_keys.append(col_str)
            
            body = statistic_table[0].find("tbody")
            if body is not None:
                players = body.find_all("tr")
                
                for player in players:
                    p_data = player.find_all("td")
                    
                    player_dict = {}

                    player_dict["pga_stat_name"] = pga_stat_name
                    player_dict["pga_stat_id"] = pga_stat_id
                    player_dict["pga_tourn_id"] = pga_tourn_id
                    player_dict["pga_season_id"] = pga_season_id

                    key_counter = 0
                    for col in p_data:
                        player_dict[data_keys[key_counter]] = col.text.strip()
                        key_counter += 1
                    data.append(player_dict)
                
        return data

def get_pgatour_statistic(url, start, end=None):
    """Get pgatour statistic over given range of season(s)

    Args:
        url (str) : base url for pga statistic

        start (int) : start season

        end (int) : end season
    
    Returns:
        dataframe of pgatour statistic over given range of season(s)
    """
    front_url = url[:url.rfind("html")]
    end_url = url[url.rfind("."): ]
    
    if end is not None:
        
        base_urls = [front_url + "y" + str(season) for season in range(start, end+1)]

        pgatour_tournaments_path = str(Path(config.RAW_DATA_DIR, "PGATOUR_tournament_ids_2017_2020.csv"))
        pgatour_ids = pd.read_csv(pgatour_tournaments_path)

        pgatour_stat_urls = []

        for url in base_urls:
            
            season_id = int(url[url.rfind("y")+1:])
            tournament_id_list = pgatour_ids["tournament_id"][pgatour_ids["season"] == season_id]

            for t_id in tournament_id_list:
                stat_url = url + ".eoff." + t_id  + end_url
                # print(stat_url)
                pgatour_stat_urls.append(stat_url)


        # tournament_id_list = pgatour_ids["tournament_id"][(pgatour_ids["season"] <= end) & (pgatour_ids["season"] >= start)].tolist()

        stat_data = [pgatour_statistic(url) for url in pgatour_stat_urls]

        # flatten data
        stat_data = list(chain.from_iterable(stat_data))

        df = pd.DataFrame(stat_data)

        return df
    
    else:

        base_url = front_url + "y" + str(start)
        # Make into a function (get stored pgatour tournament ids)
        pgatour_tournaments_path = str(Path(config.RAW_DATA_DIR, "PGATOUR_tournament_ids_2017_2020.csv"))
        pgatour_ids = pd.read_csv(pgatour_tournaments_path)

        tournament_id_list = pgatour_ids["tournament_id"][pgatour_ids["season"] == start].tolist()

        pgatour_stat_urls = [base_url + ".eoff." + t_id + end_url for t_id in tournament_id_list]
        
        stat_data = [pgatour_statistic(url) for url in pgatour_stat_urls]

        # flatten data
        stat_data = list(chain.from_iterable(stat_data))

        df = pd.DataFrame(stat_data)

        return df


def run_pgatour_metrics(metric_url, start, end=None):
    """run process of retrieving pgatour metrics and saves file using metric id in given url
    
    Args:
        metric_url (str) : pgatour metric url

        start (int) : starting pga season

        end (int) : ending pga season
    
    """
    beg_identifier = "stat."
    fname = metric_url[metric_url.rfind(beg_identifier)+len(beg_identifier):metric_url.rfind(".")]
    
    if end is not None:
        fname = f"{fname}_{start}_{end}.csv"
        pga_metric_df = get_pgatour_statistic(metric_url, start, end)

    else:
        fname = f"{fname}_{start}.csv"
        pga_metric_df = get_pgatour_statistic(metric_url, start)

    fpath = str(Path(config.RAW_PGA_METRICS_DIR, fname))
    pga_metric_df.to_csv(fpath, index=False)

def find_tourn_mapping(df1, df2, start, end=None):
    """Find tournament id mapping between espn and pgatour"""

    
    mapped_tourns = []
    if end is not None:
        seasons = [season for season in range(start, end+1)]

    else:
        seasons = [start]

    for season in seasons:
        
        if "season" in df1.columns:
            df1.rename(columns={"season":"season_id"}, inplace=True)
        
        if "season" in df2.columns:
            df2.rename(columns={"season":"season_id"}, inplace=True)

        df1_season = df1[df1.season_id==season].copy()
        df2_season = df2[df2.season_id==season].copy()
    
        missing_t_ids = df2_season["tournament_id"][~df2_season.tournament_name.apply(
                                                            lambda tournament: 
                                                            df1_season.tournament_name.str.contains(tournament, case=False)).any(1)].values
        
        matching_df = df2_season[["tournament_id", "tournament_name"]][~df2_season.tournament_id.isin(missing_t_ids)].reset_index()

        matching_df["tournament_name"] = matching_df.apply(lambda x: x["tournament_name"].lower(), axis=1)
        df1_season["tournament_name"] = df1_season.apply(lambda x: x["tournament_name"].lower(), axis=1)

        new_df = matching_df.merge(df1_season, on=["tournament_name"], suffixes=("_espn", "_pgatour")).set_index("index")

        # By keeping track of the index, I can enter column into originally passed df2 or copy of that dataframe

        new_df = new_df[["tournament_id_espn", "tournament_id_pgatour", "tournament_name", "season_id"]]
        if df1_season.shape[0] == new_df.shape[0]:
            
            mapped_tourns.append(new_df)

        else:
            print(f"dataframes have different number of tournaments. {df1_season.shape[0]} vs {new_df.shape[0]}")


    return mapped_tourns


def tournament_id_mapping(df1, df2, season):
    """Find tournament id mapping between two dataframes

    Notes:
        Currently done one season at a time.

        For current range of pga seasons, 2017 to 2020, espn tournaments
        has a larger number of tournaments

        df1 season identifer column is "season" vs df2 season identifer column is "season_id"
    
    Args:
        df1 (pd.Dataframe) : pgatour tournaments

        df2 (pd.Dataframe) : espn tournaments

        season (int) : pga season
    
    Returns:
    
    """
    df1_season = df1[df1.season==season].copy()
    df2_season = df2[df2.season_id==season].copy()

    if season == 2017:

        df2_season.replace(f"{season} Masters Tournament", "Masters Tournament", inplace=True)
        df2_season.replace("The Open", "The Open Championship", inplace=True)


        # Check shape of both df's to identify missing tournaments if need be
        # if df1_season.shape[0] != df2_season.shape[0]:
        #     missing_t_ids = df2_season[~df2_season.tournament_name.apply(lambda tournament: df1_season.tournament_name.str.contains(tournament, case=False)).any(1)].values
            
        #     matching_df = df2_season[~df2_season.tournament_id.isin(missing_t_ids)]

        # new_df = matching_df.merge(df1_season, on=["tournament_name"], suffixes=("_espn", "_pgatour"))
        # return new_df

    # Should make more robust of not having to check each season individually
    elif season == 2018:
        
        df2_season.replace(f"{season} Masters Tournament", "Masters Tournament", inplace=True)
        df2_season.replace("The Open", "The Open Championship", inplace=True)
        df2_season.replace("WGC-Bridgestone Invitational", "World Golf Championships-Bridgestone Invitational", inplace=True)
        df2_season.replace("the Memorial Tournament pres. by Nationwide", "the Memorial Tournament presented by Nationwide", inplace=True)

        # if df1_season.shape[0] != df2_season.shape[0]:
            
        #     missing_t_ids = df2_season[~df2_season.tournament_name.apply(lambda tournament: df1_season.tournament_name.str.contains(tournament, case=False)).any(1)].values

        #     matching_df = df2_season[~df2_season.tournament_id.isin(missing_t_ids)]

        # new_df = matching_df.merge(df1_season, on=["tournament_name"], suffixes=("_espn", "_pgatour"))
        # return new_df

    elif season == 2019:
        pass

    elif season == 2020:
        pass

    else:
        print("Wrong pga season entered.")


    missing_t_ids = df2_season["tournament_id"][~df2_season.tournament_name.apply(lambda tournament: df1_season.tournament_name.str.contains(tournament, case=False)).any(1)].values
    
    matching_df = df2_season[~df2_season.tournament_id.isin(missing_t_ids)]

    new_df = matching_df.merge(df1_season, on=["tournament_name"], suffixes=("_espn", "_pgatour"))
    return new_df


if __name__ == "__main__":

    espn_tournaments_path = str(Path(config.TOURNAMENTS_DIR, "espn_tournaments_2017_2020.csv"))
    espn_tourns = pd.read_csv(espn_tournaments_path)

    altered_tourn_path = str(Path(config.MAPPED_TOURNAMENTS_DIR, "updated_espn_tournaments_2017_2020.csv"))
    altered_tourn_df = pd.read_csv(altered_tourn_path)

    pgatour_tournaments_path = str(Path(config.RAW_DATA_DIR, "PGATOUR_tournament_ids_2017_2020.csv"))
    pgatour_df = pd.read_csv(pgatour_tournaments_path)


    pga_seasons = espn_tourns.season_id.unique()
    start_season, end_season = pga_seasons[-1], pga_seasons[0]

    # mapped_tourns_list = find_tourn_mapping(pgatour_df, altered_tourn_df, start_season, end_season)
    # mapped_tourns_df = pd.concat(mapped_tourns_list)
    
    # mapped_tourn_path = str(Path(config.MAPPED_TOURNAMENTS_DIR, "mapped_tournament_ids_2017_2020.csv"))
    # mapped_tourns_df.to_csv(mapped_tourn_path, index=False)
    
    # ------------------------
    # PGATOUR metrics process
    # ------------------------
    # SG: Total
    # sg_total = "https://www.pgatour.com/stats/stat.02675.html"

    # SG: Tee-to-Green
    # sg_ttg = "https://www.pgatour.com/stats/stat.02674.html"

    # SG: Approach
    # sg_approach = "https://www.pgatour.com/content/pgatour/stats/stat.02568.html"

    # Greens in Regulation Percentage
    gir_percentage = "https://www.pgatour.com/stats/stat.103.html"

    # Greens in Regulation Percentage {200+, 150-175, <125, 100+, 75-100}
    gir_200 = "https://www.pgatour.com/stats/stat.326.html"
    gir_175_200 = "https://www.pgatour.com/stats/stat.327.html"
    gir_150_175 = "https://www.pgatour.com/stats/stat.328.html"
    gir_125_150 = "https://www.pgatour.com/stats/stat.329.html"
    gir_lt_125 = "https://www.pgatour.com/stats/stat.330.html"
    gir_100_125 = "https://www.pgatour.com/stats/stat.077.html"
    gir_100 = "https://www.pgatour.com/stats/stat.02332.html"
    gir_lt_100 = "https://www.pgatour.com/stats/stat.02330.html"
    gir_75_100 = "https://www.pgatour.com/stats/stat.078.html"
    gir_lt_75 = "https://www.pgatour.com/stats/stat.079.html"
    # greens or fringe in regulation
    gofir = "https://www.pgatour.com/stats/stat.02437.html"
    gir_fairway = "https://www.pgatour.com/stats/stat.190.html"
    # GIR other than fairway
    gir_ot_fairway = "https://www.pgatour.com/stats/stat.199.html"
    gir_fairway_bunker = "https://www.pgatour.com/stats/stat.02434.html"


    pga_metrics = [gir_percentage, 
                gir_200,
                gir_175_200,
                gir_150_175,
                gir_125_150,
                gir_lt_125,
                gir_100_125,
                gir_100,
                gir_lt_100,
                gir_75_100,
                gir_lt_75,
                gofir,
                gir_fairway,
                gir_ot_fairway,
                gir_fairway_bunker
                ]

    for metric in pga_metrics:
        run_pgatour_metrics(metric, start_season, end_season)
    

    
    # b_url = "https://www.pgatour.com/content/pgatour/stats/stat.02568.html"
    # pga_metric_df = get_pgatour_statistic(b_url, 2018, 2020)

    # pga_metric_df.loc[:, "pga_season_id"] = pd.to_numeric(pga_metric_df["pga_season_id"])

    # test_url = "https://www.pgatour.com/content/pgatour/stats/stat.02568.y2020.eoff.t060.html"

    # pgatour_statistic(test_url)

