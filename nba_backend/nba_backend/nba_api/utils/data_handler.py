import os
from .decade_parser import parse_decade_data, get_team_object
from .db_utils import verify_file, data_update_from_kaggle, load_data_to_db, extract_data_from_db

dirname = os.path.dirname(__file__)
db_folder_path = os.path.abspath(os.path.join(dirname, "../db"))
db_path = os.path.join(db_folder_path, "decade.sqlite")


# THE TUPLE STRUCTURE OF FETCH_DECADE_DATA RETURNS ARE USED
# TO INFORM THE DJANGO API HANDLER THAT AN UPDATE IS NEEDED
# WITHOUT ANY STOPGAP IN EXECUTION
def fetch_decade_data():
    try:
        verify_file(db_path)
    except (FileNotFoundError, ValueError) as e:
        return None, True
    try:
        decade_content = extract_data_from_db(db_path)
        return decade_content, False
    except Exception as e:
        return None, True

def force_kaggle_update():
    game_database = data_update_from_kaggle()   
    game_db_2010s = parse_decade_data(game_database)
    
    load_data_to_db(game_db_2010s, db_path)

def fetch_teams_in_year_data():
    return get_team_object()

def get_seasons_in_decade_data(decade_content):
    return list(decade_content.keys())

def fetch_season_in_decade_data(decade_content, year):
    try:
        year_content = None
        if decade_content:
            year_content = decade_content.get(year)
        return year_content
    
    except KeyError as e:
        print(f"Year not found: {str(e)}")
        return None

if __name__ == "__main__":
    decade_content = fetch_decade_data()

    if decade_content:
        print(get_seasons_in_decade_data(decade_content))
        print(fetch_season_in_decade_data(decade_content, "2010-11"))
        print(fetch_teams_in_year_data())