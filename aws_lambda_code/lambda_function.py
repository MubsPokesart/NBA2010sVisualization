import os
import json
import kaggle
import sqlite3
import pandas as pd
from dotenv import load_dotenv

def setup_kaggle_credentials():
    """Configure Kaggle API credentials from environment variables"""
    load_dotenv()
    os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
    os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

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


def download_and_process():
    """Download dataset from Kaggle and upload to S3"""
    tmp_path = '/tmp/nba.sqlite'
    
    # Download dataset
    kaggle.api.dataset_download_file(
        'wyattowalsh/basketball',
        'nba.sqlite',
        path='/tmp',
        unzip=True 
    )
    
    # Process SQLite file if needed
    conn = sqlite3.connect(tmp_path)
    
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

    conn.close()
    
    return tmp_path



def lambda_handler(event, context):
    # Download the dataset

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
