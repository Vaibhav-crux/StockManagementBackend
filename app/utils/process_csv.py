import os
import csv
import time
import multiprocessing

# Directory containing CSV files
CSV_DIRECTORY = r"D:\Project\Company Assignment\true_beacon\project\extractor"

def find_csv_files(directory):
    """Recursively find all CSV files in the specified directory and subdirectories."""
    csv_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files

def process_csv(csv_path):
    """
    Reads and processes the contents of a CSV file with specified headers.
    Combines Date and Time into a single Timestamp, removes '.NSE' from Ticker,
    and processes rows in batches to reduce I/O operations.
    """
    row_count = 0
    batch_size = 3000  # Adjust based on memory and performance needs
    rows = []
    keys = ['Ticker', 'Timestamp', 'LTP', 'BuyPrice', 'BuyQty', 'SellPrice', 'SellQty', 'LTQ', 'OpenInterest']
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            required_headers = ["Ticker", "Date", "Time", "LTP", "BuyPrice", "BuyQty", 
                                "SellPrice", "SellQty", "LTQ", "OpenInterest"]
            if not all(header in csv_reader.fieldnames for header in required_headers):
                return csv_path, 0, f"Error: CSV file {csv_path} does not have the required headers."

            print(f"\nProcessing CSV file: {csv_path}")
            for row in csv_reader:
                ticker = row['Ticker'].replace('.NSE', '')
                timestamp = f"{row['Date']} {row['Time']}"
                row_data = [ticker, timestamp] + [row[k] for k in keys[2:]]
                rows.append(', '.join(f"{k}: {v}" for k, v in zip(keys, row_data)))
                row_count += 1
                if row_count % batch_size == 0:
                    print('\n'.join(rows))
                    rows = []

            # Print any remaining rows
            if rows:
                print('\n'.join(rows))

        return csv_path, row_count, None
    except Exception as e:
        return csv_path, 0, str(e)

def main():
    # Recursively find all CSV files in the specified directory
    csv_files = find_csv_files(CSV_DIRECTORY)

    if not csv_files:
        print(f"No CSV files found in {CSV_DIRECTORY} or its subdirectories.")
        return

    start_time = time.time()

    # Process CSV files using multiprocessing
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map(process_csv, csv_files)

    # Calculate and print elapsed time
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    milliseconds = int((elapsed_time - int(elapsed_time)) * 1000)
    print(f"\n\nTotal time taken: {int(minutes)}:{int(seconds)}:{milliseconds}")

    # Print results including row counts and any errors
    total_rows = 0
    for path, count, error in results:
        if error:
            print(f"Error with {path}: {error}")
        else:
            print(f"{path}: {count} rows processed")
            total_rows += count
    
    print(f"\nTotal rows processed across all files: {total_rows}")

if __name__ == "__main__":
    main()
