import os
import pandas as pd
import glob
from tqdm import tqdm  # Import tqdm for progress bar

# Step 1: Create a directory 'stocks_data' where individual stock files will be saved.
stocks_data_dir = 'stocks_data'
os.makedirs(stocks_data_dir, exist_ok=True)

# Step 2: Function to process each day's Bhavcopy CSV and update stock data.
def process_bhavcopy_files(bhavcopy_folder):
    # Get all CSV files in the given folder
    bhavcopy_files = glob.glob(os.path.join(bhavcopy_folder, '*.csv'))

    # Dictionary to store data for each stock
    stock_data = {}

    # Initialize the progress bar with the total number of files
    for file in tqdm(bhavcopy_files, desc="Processing Bhavcopy files", unit="file"):
        try:
            # Load the Bhavcopy CSV into a pandas DataFrame
            df = pd.read_csv(file)

            # Iterate over each row in the DataFrame
            for _, row in df.iterrows():
                stock_symbol = row['SYMBOL']

                # If this stock is not in the dictionary, initialize its list
                if stock_symbol not in stock_data:
                    stock_data[stock_symbol] = []

                # Append the row (stock data) to the stock's data list
                stock_data[stock_symbol].append(row)

        except Exception as e:
            print(f"Failed to process file {file}: {e}")

    # Step 3: Save the data for each stock in its own CSV file
    for stock_symbol, rows in tqdm(stock_data.items(), desc="Saving stock data", unit="stock"):
        # Convert the list of rows for the stock into a DataFrame
        stock_df = pd.DataFrame(rows)

        # Ensure the 'DATE1' column is parsed as a datetime object
        if 'DATE1' in stock_df.columns:  # Replace 'DATE1' with the actual column name if different
            # Parse the date column to datetime format
            stock_df['DATE1'] = pd.to_datetime(stock_df['DATE1'], format='%d-%b-%Y', errors='coerce')

            # Drop rows with invalid or missing dates (NaT)
            stock_df = stock_df.dropna(subset=['DATE1'])

            # Find the oldest and newest dates
            oldest_date = stock_df['DATE1'].min()
            newest_date = stock_df['DATE1'].max()

            print(f"Sorting data for stock {stock_symbol} from {oldest_date} to {newest_date}")

            # Sort the DataFrame by the 'DATE1' column strictly in ascending chronological order
            stock_df = stock_df.sort_values(by='DATE1')

        # Define the file path for the stock's CSV file
        stock_file_path = os.path.join(stocks_data_dir, f"{stock_symbol}.csv")

        # Save the DataFrame to CSV
        stock_df.to_csv(stock_file_path, index=False)

        print(f"Data for stock {stock_symbol} saved to {stock_file_path}.")

# Path to the folder where the Bhavcopy CSV files for each day are stored
bhavcopy_folder = 'E:/DESKTOP-STUFF/py-code/bhavcopy_data'

# Process the Bhavcopy files and save each stock's data into separate CSV files
process_bhavcopy_files(bhavcopy_folder)