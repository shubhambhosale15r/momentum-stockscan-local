import subprocess
from bhav_downloader import download_bhavcopy_for_year
from stocks_data import process_bhavcopy_files
from symbol_sector import map_sector_info

def main():
    try:
        # Step 1: Download Bhavcopy files
        print("Step 1: Downloading Bhavcopy data...")
        download_bhavcopy_for_year()  # Will not proceed until this function finishes

        # Step 2: Process Bhavcopy files into stock-specific CSVs
        print("\nStep 2: Processing Bhavcopy files...")
        bhavcopy_folder = "bhavcopy_data"  # Ensure this matches the path in `bhav_downloader.py`
        process_bhavcopy_files(bhavcopy_folder)  # Execution will wait here for the function to finish

        # Step 3: Map sector names to stock-specific files
        print("\nStep 3: Mapping sector names...")
        data_dir = "stocks_data"  # Ensure this matches the path in `stocks_data.py`
        mapping_file = "E:/DESKTOP-STUFF/py-code/Equity.csv"  # Path to the equity mapping file
        map_sector_info(data_dir, mapping_file)  # Waits here until mapping is complete

        # Step 4: Launch the Streamlit app
        print("\nStep 4: Launching Streamlit app...")
        subprocess.run(["streamlit", "run", "main.py"])  # Waits for the Streamlit app process

    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()