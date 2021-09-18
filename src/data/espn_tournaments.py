
from pathlib import Path
import sys
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config
from time import strptime


import itertools
import requests
from bs4 import BeautifulSoup
import pandas as pd


def tournament_name(tourn_meta):
    """Find tournament name

    Args:
        tourn_meta (element.Tag) : child of Leaderboard__Header class

    Returns:
        tournament name
    
    """
    tourn_name = tourn_meta.find("h1").text
    return tourn_name

def parse_espn_dates(date, identifier, b_identifier=True):
    """Parse for subset date of the original date

    Args:
        date (str) - date of a tournament (ex. 'Oct 5-8 2018')
        identifier (str) - ident. to be searched for
        b_identifer (bool) - flag to tell where subset search begins

    Returns:
        subset of the date
    """
    if b_identifier:
        if date.find(identifier) != -1:
            b_idx = date.find(identifier)
            # Should return month
            n_date = date[:b_idx].rstrip()
            return n_date
        else:
            # special case of only one date in link
            b_idx = date.find(",")
            n_date = date[:b_idx]
            return n_date
    else:
        if date.find(identifier) != -1:
            a_idx = date.find(identifier)
            # Should return day
            return date[a_idx: ]
        else:
            print("Did not find identifier in string for: ", date)

def date_parser(date):
    """Reformat date for a given ESPN tournament

    Args:
        date (str) : tournament date

    Returns:
        date in new format
    """
    
    year = date[date.rfind(" ")+1:]

    month_and_day = parse_espn_dates(date, "-")
    
    day = parse_espn_dates(month_and_day, " ", b_identifier=False)
    day = day.lstrip()
    
    month = parse_espn_dates(month_and_day, " ", b_identifier=True)
    month_abr = month[:3]
    month_number = strptime(month_abr, "%b").tm_mon
    
    date_str = str(month_number) + "/" + day + "/" + year
    return date_str

def tournament_date(tourn_meta):
    """Get tournament date and reformat 

    Args:
        tourn_meta (element.Tag) : child of Leaderboard__Header class

    Returns:
        tournament date
    """
    tourn_date = tourn_meta.find("span").text
    t_date = date_parser(tourn_date)
    return t_date

def tournament_purse(tourn_header):
    """Get tournament purse size

    Args:
        tourn_header (element.Tag) : Leaderboard__Header class

    Returns:
        tournament purse
    
    """
    purse_class = tourn_header.find("div", class_="n7 clr-gray-04").text
    # string find method
    purse_start = purse_class.find("$") + 1
    purse_end = purse_class.find("D")
    purse = purse_class[purse_start:purse_end]
    purse = purse.replace(",", "")

    return purse

def players_purse(t_body):
    """Get each players purse size and aggregate for total purse size

    Args:
        t_body (element.Tag) : 
    Returns:
        tournament purse size
    """
    purse_size = 0
    players = t_body.find_all("tr", class_="Table__TR Table__even")
    if players is not None:
        
        for player in players:
            p_results = player.find_all("td", class_="Table__TD")
            # winnings entry
            p_winnings = p_results[-2].text
            if p_winnings == "--":
                purse_size += 0
            else:
                p_winnings = p_winnings[1:]
                p_winnings = p_winnings.replace(",", "")
                winnings = int(p_winnings)
                purse_size += winnings
        
    return purse_size

def players_in_tournament(t_body):
    """Get number of players in a tournament
    
    Args:
        t_body (element.tag) : tourn table body. Child of ResponsiveTable
    
    Returns:
        number of players
    """
    players = t_body.find_all("tr", class_="Table__TR Table__even")
    if players is not None:
        num_players = len(players)
        return num_players

def tournament_winner_name(t_body):
    """Get tournament winner name
    
    Args:
        t_body (element.tag) : tourn table body. Child of ResponsiveTable
    
    Returns:
        winner name if found, else None
    """
    winner = t_body.find("a")
    if winner:
        name = winner.text
        return name
    else:
        return None

def tournament_winner_id(t_body):
    """Get tournament winner id

    Args:
        t_body (element.tag) : tourn table body. Child of ResponsiveTable

    Returns:
        tournament winner id
    """
    winner = t_body.find("a")
    if winner:
        winner_id = winner["href"]
        # substring start and end indexes
        start_winner = winner_id.find("id/") + 3
        end_winner = winner_id.rfind("/")

        id = winner_id[start_winner:end_winner]
        return id
    else:
        return None

def winning_score(t_body):
    """Get winning score total for tournament

    Args:
        t_body (element.tag) : tourn table body. Child of ResponsiveTable

    Returns
        winning score total
    """
    
    # tournament winner's total's data
    tourn_totals = t_body.find("td", class_="Table__TD")
    if tourn_totals:
        totals = tourn_totals.find_next_siblings()
        if len(totals) == 9:
            # selects 4 round (72 hole) total
            total = totals[-3].text

            return total
        else:
            total = totals[-3].text
            if len(total) == 0:
                return None
            else:
                return total
    

def tournament_information(url, s_id):
    """Gets tournament meta information including the following,
        
        tournament meta = {
            tournament id,
            name,
            date,
            purse,
            winning score,
            winner name,
            winner id,
            season id
        }

    Args:
        url (str): espn tournament webpage

    Returns:
        A dictionary of tournament meta information
    """
    tourn_info = {}

    
    base_url = url
    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, "html.parser")

    # tourn name, date and purse
    header = soup.find("div", class_="Leaderboard__Header")

    mt4 = header.find_all("div", class_="mt4")
    tourn_meta = mt4[-1]

    t_id = url[url.rfind("=") + 1:]
    tourn_info["tournament_id"] = t_id

    t_name = tournament_name(tourn_meta)
    tourn_info["tournament_name"] = t_name

    t_date = tournament_date(tourn_meta)
    tourn_info["date"] = t_date

    t_purse = tournament_purse(header)
    tourn_info["tournament_purse"] = t_purse

    # Table's on webpage. index with -1 in case of playoff table
    tourn_tables = soup.select("div.ResponsiveTable")
    if tourn_tables:
        # win_total, tournamnet_size, winner_name, winner_id
        tourn_table = tourn_tables[-1]

        tourn_body = tourn_table.find("tbody", class_="Table__TBODY")

        t_win_score = winning_score(tourn_body)
        tourn_info["win_total"] = t_win_score

        t_player_size = players_in_tournament(tourn_body)
        tourn_info["tournament_size"] = t_player_size

        t_win_name = tournament_winner_name(tourn_body)
        tourn_info["winner_name"] = t_win_name

        t_win_id = tournament_winner_id(tourn_body)
        tourn_info["winner_id"] = t_win_id

        tourn_info["season_id"] = s_id

        
        if t_id == "2277":
            tourn_info["winner_name"] = "Scott Piercy"

            tourn_info["winner_id"] = "1037"

            tourn_info["win_total"] = "265"

        return tourn_info
    else:
        print(f"No div.ResponsiveTable, (Tournament {t_id} Cancelled)")

        tourn_info["win_total"] = None
        tourn_info["tournament_size"] = None
        tourn_info["winner_name"] = None
        tourn_info["winner_id"] = None
        tourn_info["season_id"] = s_id

        return tourn_info

def espn_season_schedule(season_url):
    """Get all tournaments in the season with their specific identifiers
    
    Args:
        season_url (str) : espn season schedule webpage

    Returns:
        collection of espn tournament data
    """
    
    page = requests.get(season_url)
    soup = BeautifulSoup(page.content, "html.parser")

    season_table = soup.select("div.ResponsiveTable")
    if season_table is not None:
        season_body = season_table[0].find("tbody", class_="Table__TBODY")

    tournament_data = []
    
    tournaments = season_body.find_all("div", class_="eventAndLocation__innerCell")
    
    if tournaments is not None:
        for tournament in tournaments:
            tournament_url = tournament.find("a")
            if tournament_url:    
                t_url = tournament_url["href"]
                print(f"Fetching {t_url} data")

                season_id = season_url[season_url.rfind("/")+1 :]
                t_data = tournament_information(t_url, season_id)
                tournament_data.append(t_data)

        return tournament_data

def espn_schedule_runner():
    """Run schedule runner over range of pga seasons
       from espn and save data.
       
    """
    # Imporvement -> Ask from cmdline for season range
    pga_season_urls = [
        "https://www.espn.com/golf/schedule/_/season/2020",
        "https://www.espn.com/golf/schedule/_/season/2019",
        "https://www.espn.com/golf/schedule/_/season/2018",
        "https://www.espn.com/golf/schedule/_/season/2017"
    ]

    pga_tournament_data = [espn_season_schedule(pga_season) for pga_season in pga_season_urls]

    # Flatten nested list of pga seasons
    pga_tournament_data = list(itertools.chain.from_iterable(pga_tournament_data))
    

    df = pd.DataFrame(pga_tournament_data)
    df["tournament_purse"] = pd.to_numeric(df["tournament_purse"], downcast="integer")
    df["win_total"] = pd.to_numeric(df["win_total"], downcast="integer")
    df["date"] = pd.to_datetime(df["date"])
    
    file_path = str(Path(config.RAW_DATA_DIR, "espn_tournaments_2017_2020.csv"))

    df.to_csv(file_path, index=False)

def get_espn_schedule(start, end=None):
    """
    
    """
    b_url = "https://www.espn.com/golf/schedule/_/season/"
    if end is not None:
        pga_season_urls = [b_url + str(season) for season in range(start, end+1)]
        file_path = str(Path(config.RAW_DATA_DIR, f"espn_tournaments_{start}_{end}.csv"))

    else:
        pga_season_urls = [f"{b_url}{start}"]
        file_path = str(Path(config.RAW_DATA_DIR, f"espn_tournaments_{start}.csv"))

    pga_tournament_data = [espn_season_schedule(pga_season) for pga_season in pga_season_urls]

    # Flatten nested list of pga seasons
    pga_tournament_data = list(itertools.chain.from_iterable(pga_tournament_data))
    
    df = pd.DataFrame(pga_tournament_data)
    df["tournament_purse"] = pd.to_numeric(df["tournament_purse"], downcast="integer")
    df["win_total"] = pd.to_numeric(df["win_total"], downcast="integer")
    df["date"] = pd.to_datetime(df["date"])
    
    df.to_csv(file_path, index=False)

def filter_valid_tournaments(df):
    """Filter for valid tournaments

    Notes:
        Excluding Tour championship for 2019 and 2020
        due to rule change in score totals.

    Args:
        df (pd.DataFrame) : espn tournaments

    Returns:
        valid_df (pd.Dataframe) : valid espn tournaments

    """
    valid_df = df[~df.winner_name.isnull()].copy()
    valid_df = valid_df[~((valid_df["tournament_id"] == 401056542) | (valid_df["tournament_id"] == 401155476))]

    return valid_df

def filter_tournaments(df):
    """Filter espn tournaments.
    
    Notes:
        differs from filter_valid_tournaments by keeping the Tour Championship in the set.
        The reason for the removal of that tournament is the rule changed that started in 2019
        
    Args:
        df (pd.DataFrame): espn tournaments
        
    Returns:
        filtered dataframe of espn tournaments    
    """
    filtered_df = df[~df.winner_name.isnull()].copy()
    
    return filtered_df

def create_subset_tournaments(tourn_path, subset_path, valid_tourns=True):
    """Create subset of tournaments to save
    
    Args:
        tourn_path (str) : espn tournaments file name

        subset_path (str) : subset tournaments file name

    """
    espn_tournaments_path = str(Path(config.RAW_DATA_DIR, tourn_path))
    
    df = pd.read_csv(espn_tournaments_path, parse_dates=["date"])

    if valid_tourns == True:

        subset_tournaments_df = filter_valid_tournaments(df)

    else:

        subset_tournaments_df = filter_tournaments(df)


    subset_tournaments_path = str(Path(config.TOURNAMENTS_DIR, subset_path))

    subset_tournaments_df.to_csv(subset_tournaments_path, index=False)

def alter_tournament_names(df, fname=None):
    """Change espn tournament names to match more closely to pgatour's conventions
    
    Args:
        df (pd.DataFrame) : espn tournaments

        fname (str) : file name, optional arg
    Returns:
    
    """
    seasons = df.season_id.unique()

    for season in seasons:
        df.replace(f"{season} Masters Tournament", "Masters Tournament", inplace=True)

    wgc_tournaments = df[["tournament_name"]][df.tournament_name.str.contains("WGC-")]
    wgc_tournaments.loc[:, "tournament_name"] = wgc_tournaments.tournament_name.apply(lambda x: x.replace("WGC-", "World Golf Championship-"))
    df.loc[wgc_tournaments.index, "tournament_name"] = wgc_tournaments

    df.replace("The Open", "The Open Championship", inplace=True)
    df.replace("Arnold Palmer Invitational Pres.", "Arnold Palmer Invitational presented", inplace=True)
    df.replace("the Memorial Tournament pres.", "the Memorial Tournament presented", inplace=True)
    df.replace("Shriners Hospital for Children Open", "Shriners Hospitals for Children Open", inplace=True)
    df.replace("THE ZOZO CHAMPIONSHIP", "ZOZO CHAMPIONSHIP", inplace=True)

    if fname is not None:
        a_tourn_path = str(Path(config.MAPPED_TOURNAMENTS_DIR, fname))

        df.to_csv(a_tourn_path, index=False)


if __name__ == "__main__":
    
    espn_tournaments_path = str(Path(config.RAW_DATA_DIR, "espn_tournaments_2017_2020.csv"))
    
    espn_df = pd.read_csv(espn_tournaments_path, parse_dates=["date"])

    # valid_tournaments_df = filter_valid_tournaments(df)

    # valid_tournaments_path = str(Path(config.TOURNAMENTS_DIR, "valid_tournaments_2017_2020.csv"))

    # valid_tournaments_df.to_csv(valid_tournaments_path, index=False)
    
    # get_espn_schedule(2011, 2016)

    alter_tournament_names(espn_df, "updated_espn_tournaments_2017_2020.csv")