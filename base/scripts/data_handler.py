import os
import json
import sqlite3
import numpy as np
import pandas as pd
from decade_parser import parse_decade_data
from db_utils import verify_file, data_update_from_kaggle, load_data_to_db, extract_data_from_db

dirname = os.path.dirname(__file__)
db_folder_path = os.path.abspath(os.path.join(dirname, "../db"))
db_path = os.path.join(db_folder_path, "decade.sqlite")

def fetch_decade_data():
    decade_content = None
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
    
    decade_content = extract_data_from_db(db_path)
    return decade_content

def force_kaggle_update():
    game_database = data_update_from_kaggle()   
    game_db_2010s = parse_decade_data(game_database)
    
    load_data_to_db(game_db_2010s, db_path)


if __name__ == "__main__":
    decade_content = fetch_decade_data()
    print(decade_content)