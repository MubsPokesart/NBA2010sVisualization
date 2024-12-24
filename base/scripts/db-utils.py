import os
import kaggle
import sqlite3
import zipfile
import pandas as pd

# CURRENT STATUS: THIS SCRIPT IS NOT WORKING
# MAIN ERROR STEMS FROM THE DOWNLOAD OF THE SQLITE FILE
# THE FILE RETURNS EMPTY OR USED BY ANOTHER PROCESS


dirname = os.path.dirname(__file__)

def data_update():
    kaggle.api.authenticate()

    data_dir = os.path.abspath(os.path.join(dirname, "../db/temporary_kaggle_files"))
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        # Force the download and unzip
        kaggle.api.dataset_download_file(
            'wyattowalsh/basketball', 
            'nba.sqlite', 
            path=data_dir,
            force=True 
        )
        
        zip_path = os.path.join(data_dir, 'nba.sqlite.zip')

        # Verify file exists and has content
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Zip file not found at {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        
        sql_path = os.path.join(data_dir, 'nba.sqlite')
        # Verify file exists and has content
        if not os.path.exists(sql_path):
            raise FileNotFoundError(f"SQLite file not found at {sql_path}")
            
        file_size = os.path.getsize(sql_path)
        print(f"Downloaded file size: {file_size} bytes")
        
        if file_size == 0:
            raise ValueError("Downloaded file is empty (0 bytes)")

        # Connect to database
        conn = sqlite3.connect(sql_path)
        query = "SELECT * FROM game"
        df = pd.read_sql_query(query, conn)
        conn.close()
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"Error during download/processing: {str(e)}")
        if 'conn' in locals():
            conn.close()
        raise e
    finally:
        # Cleanup
        try:
            for file in os.listdir(data_dir):
                file_path = os.path.join(data_dir, file)
                os.remove(file_path)
        except Exception as cleanup_error:
            print(f"Error during cleanup: {str(cleanup_error)}")

if __name__ == '__main__':
    df = data_update()