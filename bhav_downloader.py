import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from tqdm import tqdm
import time


# Function to generate the URL for the Bhavcopy data based on the date
def generate_bhavcopy_url(date):
    return f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date.strftime('%d%m%Y')}.csv"


# Function to download the Bhavcopy data for a specific date with retry logic and browser-like headers
def download_bhavcopy(url, local_file_path, retries=3, timeout=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                with open(local_file_path, "wb") as file:
                    file.write(response.content)
                print(f"File downloaded successfully: {local_file_path}")
                return True
            elif response.status_code == 404:
                print(f"File not found for {url} (404). Skipping this date.")
                return False
            else:
                print(f"Failed to download file for {url}. HTTP Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {url} with error: {e}")
            attempt += 1
            time.sleep(2)  # Sleep for 2 seconds before retrying
    return False





# Function to download Bhavcopy for the past year with progress bar
def download_bhavcopy_for_year():
    # Get today's date
    end_date = datetime.today()

    # Get the date 1 year ago from today
    start_date = end_date - timedelta(days=365)

    # Create a directory to store the files
    download_dir = "bhavcopy_data"
    os.makedirs(download_dir, exist_ok=True)

    # Calculate total days to download
    total_days = (end_date - start_date).days + 1

    # Initialize tqdm for the progress bar
    with tqdm(total=total_days, desc="Downloading Bhavcopy Data", unit="day") as pbar:
        # Loop through each day from the start date to the end date
        current_date = start_date
        while current_date <= end_date:
            # Generate the URL for the current date
            url = generate_bhavcopy_url(current_date)

            # Define the file path to save the downloaded CSV
            local_file_path = os.path.join(download_dir, f"bhavcopy_{current_date.strftime('%d%m%Y')}.csv")

            # Download the Bhavcopy data with retries
            success = download_bhavcopy(url, local_file_path)

            if success:
                # Read and display a sample of the downloaded CSV
                pass
            else:
                print(f"Skipping {current_date.strftime('%d%m%Y')} due to download failure.")

            # Manually update the progress bar after each download attempt
            pbar.update(1)

            # Move to the next day
            current_date += timedelta(days=1)


if __name__ == "__main__":
    download_bhavcopy_for_year()