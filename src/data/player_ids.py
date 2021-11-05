import os
from pathlib import Path
import re
import sys
sys.path.append("c:\\Users\\kpdav\\machine_learning\\projects\\PGA-portfolio-optimizer\\config")
import config
from historical_data import find_player_id

import requests
from bs4 import BeautifulSoup
import pandas as pd


def espn_player_ids():
    """Get all player id's from espn player's page
    

    Returns:
        dictonary of player id's
    """
    player_id_page = "https://www.espn.com/golf/players"
    with requests.Session() as session:

        page = session.get(player_id_page) 

        if page.status_code == 200:
            
            soup = BeautifulSoup(page.content, "lxml")
            base = soup.find("table", class_="tablehead")
            
            player_id_dict = {}
            if base is not None:
                players = base.find_all("tr", class_=re.compile("player"))
                
                for player in players:
                    p_link = player.find("a", href=True)["href"]

                    p_id = find_player_id(p_link)
                    p_name = p_link[p_link.rfind("/")+1:]
                    p_name = p_name.replace("-", " ")

                    player_id_dict[int(p_id)] = [p_name]

            return player_id_dict
        else:
            print("Could not access page")

def save_data(data, filename):
    """Save data to disk
    
    Args:
        
        data (dict)

        filename(str)
        
    """
    
    df = pd.DataFrame.from_dict(data, orient="index").reset_index()
    df = df.rename(columns={"index":"player_id", 0:"player_name"})
    f_path = str(Path(config.RAW_PLAYER_ID_DIR, filename))
    
    df.to_csv(f_path, index=False)


def main():
    
    espn_pids = espn_player_ids()
    save_data(espn_pids, "espn_player_ids.csv")


if __name__ == "__main__":
    main()