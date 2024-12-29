import os
import time
import kaggle
import sqlite3
import zipfile
import numpy as np
import pandas as pd
from collections import defaultdict
from contextlib import contextmanager

dirname = os.path.dirname(__file__)

# General sql and file utility functions

@contextmanager
def sqlite_connection(db_path, timeout=30):
    """Context manager for SQLite connections with timeout and error handling"""
    conn = None
    try:
        conn = sqlite3.connect(db_path, timeout=timeout)
        yield conn
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            raise Exception("Database is locked. Please try again later.") from e
        raise
    finally:
        if conn:
            conn.close()

def verify_file(file_path, min_size=1024):  # 1KB minimum
    """Verify file exists and meets minimum size requirements"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at {file_path}")
    
    file_size = os.path.getsize(file_path)
    if file_size < min_size:
        raise ValueError(f"File is too small ({file_size} bytes). Minimum size is {min_size} bytes")
    
    return file_size

def safe_cleanup(directory):
    """Safely cleanup files in directory"""
    if not os.path.exists(directory):
        return
        
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except PermissionError:
            print(f"Warning: Could not remove {file_path} due to permissions")
        except Exception as e:
            print(f"Warning: Failed to remove {file_path}: {str(e)}")

# Kaggle based utility functions
def data_update_from_kaggle(max_retries=3, retry_delay=1):
    kaggle.api.authenticate()

    data_dir = os.path.abspath(os.path.join(dirname, "../db/temporary_kaggle_files"))
    os.makedirs(data_dir, exist_ok=True)
    
    conn = None
    attempts = 0
    
    try:
        # Download with retry logic
        while attempts < max_retries:
            try:
                kaggle.api.dataset_download_file(
                    'wyattowalsh/basketball', 
                    'nba.sqlite', 
                    path=data_dir,
                    force=True 
                )
                break
            except Exception as e:
                attempts += 1
                if attempts == max_retries:
                    raise Exception(f"Failed to download after {max_retries} attempts") from e
                print(f"Download attempt {attempts} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        
        zip_path = os.path.join(data_dir, 'nba.sqlite.zip')
        verify_file(zip_path)
        
        # Extract with verification
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Verify zip file integrity
            if zip_ref.testzip() is not None:
                raise zipfile.BadZipFile("Zip file is corrupted")
            zip_ref.extractall(data_dir)
        
        sql_path = os.path.join(data_dir, 'nba.sqlite')
        file_size = verify_file(sql_path)
        print(f"SQLite database size: {file_size:,} bytes")

        # Use context manager for database connection
        with sqlite_connection(sql_path) as conn:
            # Verify table exists
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='game'")
            if cursor.fetchone()[0] == 0:
                raise ValueError("The 'game' table does not exist in the database")
            
            # Get table info for verification
            cursor.execute("PRAGMA table_info(game)")
            columns = cursor.fetchall()
            if not columns:
                raise ValueError("The 'game' table appears to be empty or corrupted")
            
            # Read data
            query = "SELECT * FROM game"
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                raise ValueError("No data retrieved from the game table")
                
            print(f"Successfully retrieved {len(df)} rows")
            print(df.head())
            
            return df

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise

    finally:
        safe_cleanup(data_dir)

# NBA Database parsing utility functions
def create_schema(conn):
    """Create the database schema."""
    cursor = conn.cursor()   
    with open(os.path.join(dirname, "db_create.sql"), 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
        cursor.executemany(
        "INSERT OR IGNORE INTO Conferences (conference_id, conference_name) VALUES (?, ?)",
        [('W', 'Western'), ('E', 'Eastern')]
        )
    conn.commit()

def insert_seasons(conn, seasons_data):
    """Insert seasons into the database."""
    cursor = conn.cursor()
    seasons = [(season,
               int(season.split('-')[0]),
               2000 + int(season.split('-')[1]))
              for season in seasons_data.keys()]
    cursor.executemany(
        "INSERT OR IGNORE INTO Seasons (season_id, start_year, end_year) VALUES (?, ?, ?)",
        seasons
    )
    conn.commit()

def insert_teams(conn, data):
    """Insert teams into the database."""
    cursor = conn.cursor()
    # Collect unique teams with their conferences
    teams = set()
    for season_data in data.values():
        for team_data in season_data:
            teams.add((team_data['team'], team_data['conference'][0]))  # Use first letter of conference as ID
    # Insert teams
    cursor.executemany(
        "INSERT OR IGNORE INTO Teams (team_name, conference_id) VALUES (?, ?)",
        list(teams)
    )
    conn.commit()

def insert_team_stats(conn, data):
    """Insert team statistics into the database."""
    cursor = conn.cursor()
    
    # Get team_id mapping
    cursor.execute("SELECT team_id, team_name FROM Teams")
    team_mapping = {name: id for id, name in cursor.fetchall()}
    
    # Prepare stats data
    stats_data = []
    for season_id, season_data in data.items():
        for team_data in season_data:
            team_id = team_mapping[team_data['team']]
            stats_data.append((
                team_id,
                season_id,
                float(team_data['average_offensive_rating']),
                float(team_data['average_defensive_rating']),
                float(team_data['average_net_rating']),
                float(team_data['average_plus_minus']),
                float(team_data['relative_net_rating']),
                float(team_data['relative_offensive_rating']),
                float(team_data['relative_defensive_rating'])
            ))
    
    # Insert stats
    cursor.executemany("""
        INSERT OR REPLACE INTO TeamStats (
            team_id, season_id,
            average_offensive_rating, average_defensive_rating,
            average_net_rating, average_plus_minus,
            relative_net_rating, relative_offensive_rating,
            relative_defensive_rating
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, stats_data)
    
    conn.commit()

def load_data_to_db(data_object, db_path): 
    # Connect to database
    conn = sqlite3.connect(db_path) 

    try:
        # Create schema
        create_schema(conn)
        
        # Insert data
        insert_seasons(conn, data_object)
        insert_teams(conn, data_object)
        insert_team_stats(conn, data_object)
        
        print(f"Successfully loaded data into {db_path}")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def extract_data_from_db(db_path):
    """
    Extract data from the SQLite database and format it exactly like the original dictionary.
    Returns a dictionary with the same structure as the input data.
    """

    with sqlite_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Get all seasons ordered chronologically
        cursor.execute("SELECT season_id FROM Seasons ORDER BY start_year, end_year")
        seasons = [row[0] for row in cursor.fetchall()]
        
        # Initialize the result dictionary using defaultdict
        result = defaultdict(list)
        
        # Query to get all data for each season
        query = """
        SELECT 
            s.season_id,
            t.team_name,
            t.conference_id,
            ts.average_offensive_rating,
            ts.average_defensive_rating,
            ts.average_net_rating,
            ts.average_plus_minus,
            ts.relative_net_rating,
            ts.relative_offensive_rating,
            ts.relative_defensive_rating
        FROM TeamStats ts
        JOIN Teams t ON ts.team_id = t.team_id
        JOIN Seasons s ON ts.season_id = s.season_id
        JOIN Conferences c ON t.conference_id = c.conference_id
        ORDER BY s.season_id, t.team_name
        """
        
        cursor.execute(query)
        
        # Conference mapping from ID to full name
        conf_mapping = {'W': 'Western', 'E': 'Eastern'}
        
        # Process each row and build the dictionary
        for row in cursor.fetchall():
            season_id, team_name, conf_id, *stats = row
            
            # Create the team dictionary with exact same structure
            team_dict = {
                'team': team_name,
                'conference': conf_mapping[conf_id],
                'average_offensive_rating': np.float64(stats[0]),
                'average_defensive_rating': np.float64(stats[1]),
                'average_net_rating': np.float64(stats[2]),
                'average_plus_minus': np.float64(stats[3]),
                'relative_net_rating': np.float64(stats[4]),
                'relative_offensive_rating': np.float64(stats[5]),
                'relative_defensive_rating': np.float64(stats[6])
            }
            
            result[season_id].append(team_dict)
        
        conn.close()
    
    # Convert defaultdict to regular dict
    return dict(result)