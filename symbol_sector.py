import os
import pandas as pd

# Paths (customize these to your directories)
data_dir = 'E:/DESKTOP-STUFF/py-code/stocks_data'       # directory containing stock symbol CSVs
mapping_file = 'E:/DESKTOP-STUFF/py-code/Equity.csv'         # mapping CSV with security details

def map_sector_info(data_dir, mapping_file):
    data_dir = 'E:/DESKTOP-STUFF/py-code/stocks_data'       # directory containing stock symbol CSVs
    mapping_file = 'E:/DESKTOP-STUFF/py-code/Equity.csv'         # mapping CSV with security details


# Read the mapping CSV into a pandas DataFrame
    mapping_df = pd.read_csv(mapping_file)

# Create a dictionary mapping each stock symbol (Security Id) to its ISubgroup Name
# Ensure that the column names match exactly with your CSV (here they are 'Security Id' and 'ISubgroup Name')
    symbol_to_subgroup = mapping_df.set_index('Security Id')['Industry New Name'].to_dict()

    # Process each CSV file in the directory
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            # Extract symbol from filename (e.g., ABB.csv becomes 'ABB')
            symbol = os.path.splitext(filename)[0]
            csv_path = os.path.join(data_dir, filename)
            
            # Load the CSV file for the specific stock symbol
            df = pd.read_csv(csv_path)
            
            # Lookup the ISubgroup Name from the mapping
            subgroup = symbol_to_subgroup.get(symbol)
            
            if subgroup:
                # If a matching symbol is found, create a new column "Sector Name" with the subgroup value
                df['Sector Name'] = subgroup
            else:
                # Option: if no match is found, you might either assign a default value or leave it as None/NaN
                df['Sector Name'] = None
            
            if df['Sector Name'].dropna().empty or  all(df['Sector Name'] == '-') :
                # If all values are missing, remove the CSV file
                print(f"Removing file: {csv_path} (Sector Name is empty)")
                os.remove(csv_path)
            else:
                # Otherwise, save the updated dataframe back to disk (overwrite the original file)
                df.to_csv(csv_path, index=False)
