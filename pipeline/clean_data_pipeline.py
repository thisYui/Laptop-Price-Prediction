import pandas as pd
import os
import sys

# Add the project root to the sys.path to allow importing from scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the orchestrator function from our scripts folder
from scripts.data_cleaning import process_all_features

def run_cleaning_pipeline(input_path, output_path):
    print(f"Reading data from {input_path}...")
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
        
    print("Initial shape:", df.shape)
    
    # Process the data using the script functions
    df = process_all_features(df)
    
    # Validation step
    print("Missing values in shop prices after cleaning:")
    print(df[['shop_1_price', 'shop_2_price', 'shop_3_price']].isnull().sum())
    print("Cleaned shape:", df.shape)

    # Save to processed directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Saved cleaned data to {output_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, "..", "data", "raw", "laptop_features.csv")
    output_file = os.path.join(current_dir, "..", "data", "raw", "clean_laptop_features.csv")
    run_cleaning_pipeline(input_file, output_file)
