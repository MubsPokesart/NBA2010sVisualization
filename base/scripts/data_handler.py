import os
import json
import sqlite3
import numpy as np
import pandas as pd
from db_utils import verify_file, data_update_from_kaggle, sqlite_connection
from decade_parser import process_filter_db, generate_dataframe_metrics, generate_individual_season_metrics, generate_relative_metrics

dirname = os.path.dirname(__file__)
db_folder_path = os.path.abspath(os.path.join(dirname, "../db"))
db_path = os.path.join(db_folder_path, "decade.sqlite")

def fetch_decade_data():
    try:
        verify_file(db_path)
    except FileNotFoundError as e:
        print(f"File not found: {str(e)}")        
        force_kaggle_update()
        return
    except ValueError as e:
        print(f"Invalid file: {str(e)}")
        force_kaggle_update()
        return
    
    with sqlite_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM game_info")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        df = pd.DataFrame(rows, columns=columns)




    return db_path

def force_kaggle_update():

    data_update_from_kaggle()



# Process data and filter based on date
range_dataframe, team_objects = process_filter_db(db_path)

# Generate possession-based metrics for each game
team_objects = generate_dataframe_metrics(range_dataframe, team_objects)

# Generate possession-based metrics for each team in each season
seasons_dict = generate_individual_season_metrics(team_objects)

# Add relative net rating to each season
seasons_dict = generate_relative_metrics(seasons_dict)

# Output the results
print(seasons_dict)