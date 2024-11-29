import requests
import json
import pandas as pd
import ijson
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import psycopg2
from .db import get_session

def get_scryfall_bulk_data():
    # Get the bulk data information
    bulk_data_url = "https://api.scryfall.com/bulk-data"
    response = requests.get(bulk_data_url)
    
    if response.status_code != 200:
        print(f"Error fetching bulk data: {response.status_code}")
        return None
    
    bulk_data = response.json()
    
    # Find the "all cards" data object
    all_cards_data = next(
        (item for item in bulk_data['data'] if item['type'] == 'all_cards'),
        None
    )
    
    if all_cards_data:
        print(f"Found all cards data. Download URI: {all_cards_data['download_uri']}")
        print(f"Size: {all_cards_data['size']} bytes")
        print(f"Updated at: {all_cards_data['updated_at']}")
        
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Download the file
        filename = os.path.join(data_dir, "all_cards.json")
        print(f"Downloading to {filename}...")
        
        response = requests.get(all_cards_data['download_uri'], stream=True)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Download complete: {filename}")
        all_cards_data['local_file'] = filename
        return all_cards_data
    else:
        print("Could not find all cards data")
        return None

def put_data_in_df(all_cards_data):
    if 'local_file' not in all_cards_data:
        print("Error: Local file not found. Please download the data first.")
        return None
        
    filename = all_cards_data['local_file']
    if not os.path.exists(filename):
        print(f"Error: File {filename} does not exist")
        return None
    
    # Create empty lists to store the data
    data_list = []
    
    try:
        # Open and parse the local file
        with open(filename, 'rb') as f:
            parser = ijson.parse(f)
            current_item = {}
            
            for prefix, event, value in parser:
                try:
                    if prefix.endswith('.item'):  # Adjust this based on your JSON structure
                        if event == 'start_map':
                            current_item = {}
                        elif event == 'end_map':
                            data_list.append(current_item)
                            if len(data_list) >= 1000:  # Process in chunks of 1000
                                chunk_df = pd.DataFrame(data_list)
                                if 'df' not in locals():
                                    df = chunk_df
                                else:
                                    df = pd.concat([df, chunk_df], ignore_index=True)
                                data_list = []
                    elif '.' in prefix:  # This handles nested values
                        key = prefix.split('.')[-1]
                        current_item[key] = value
                except ijson.common.IncompleteJSONError as e:
                    print(f"Incomplete JSON error: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing JSON item: {e}")
                    continue
                    
        # Handle any remaining data
        if data_list:
            chunk_df = pd.DataFrame(data_list)
            if 'df' not in locals():
                df = chunk_df
            else:
                df = pd.concat([df, chunk_df], ignore_index=True)
    
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None
    
    print("Data added to dataframe")
    return df

def process_data(df):
    # First parse the prices column if it's a string
    if df['prices'].dtype == 'object':
        df['prices'] = df['prices'].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
    
    # Extract price columns from the dictionary in 'prices'
    df['usd'] = df['prices'].apply(lambda x: x.get('usd') if isinstance(x, dict) else None)
    df['usd_foil'] = df['prices'].apply(lambda x: x.get('usd_foil') if isinstance(x, dict) else None)
    df['usd_etched'] = df['prices'].apply(lambda x: x.get('usd_etched') if isinstance(x, dict) else None)
    df['eur'] = df['prices'].apply(lambda x: x.get('eur') if isinstance(x, dict) else None)
    df['eur_foil'] = df['prices'].apply(lambda x: x.get('eur_foil') if isinstance(x, dict) else None)
    df['tix'] = df['prices'].apply(lambda x: x.get('tix') if isinstance(x, dict) else None)
    
    # Convert price strings to float, handling None values
    price_columns = ['usd', 'usd_foil', 'usd_etched', 'eur', 'eur_foil', 'tix']
    for col in price_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['image_small'] = df['image_uris'].apply(lambda x: x.get('small') if isinstance(x, dict) else None)
    df['image_normal'] = df['image_uris'].apply(lambda x: x.get('normal') if isinstance(x, dict) else None)
    df['image_large'] = df['image_uris'].apply(lambda x: x.get('large') if isinstance(x, dict) else None)
    df['image_png'] = df['image_uris'].apply(lambda x: x.get('png') if isinstance(x, dict) else None)
    df['image_artcrop'] = df['image_uris'].apply(lambda x: x.get('art_crop') if isinstance(x, dict) else None)
    df['image_bordercrop'] = df['image_uris'].apply(lambda x: x.get('border_crop') if isinstance(x, dict) else None)
    
    return df

session = get_session

def put_data_in_db(df):
    df.to_sql('all_cards', session, index=False, if_exists='replace')
    session.commit()
    print("Data added to database")


if __name__ == "__main__":
    bulk_data = get_scryfall_bulk_data()
    df = put_data_in_df(bulk_data)
    df = process_data(df)
    put_data_in_db(df)

    session.close()
