import os
import kaggle
import sqlite3
import zipfile
import pandas as pd
import time
from contextlib import contextmanager

dirname = os.path.dirname(__file__)

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

def data_update(max_retries=3, retry_delay=1):
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

if __name__ == '__main__':
    try:
        df = data_update()
    except Exception as e:
        print(f"Failed to update data: {str(e)}")
        raise