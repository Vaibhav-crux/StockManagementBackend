import os
import csv
import time
import multiprocessing
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.db.models.ticks import Ticks
from app.db.models.orders import Orders
from app.config.db_connection import get_db_connection

# Directory containing CSV files
CSV_DIRECTORY = r"D:\Project\Company Assignment\true_beacon\project\extractor"

# Batch size for database commits
BATCH_SIZE = 5000  # Increased batch size

def find_csv_files(directory):
    """Recursively find all CSV files in the specified directory and subdirectories."""
    csv_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    return csv_files

def init_db():
    """Initialize the database engine and session for each process."""
    db_connection_string, ssl_args = get_db_connection()
    engine = create_engine(db_connection_string, connect_args=ssl_args)
    return engine

def process_csv(csv_path):
    """
    Reads and processes the contents of a CSV file with specified headers.
    Combines Date and Time into a single Timestamp, removes '.NSE' from Ticker,
    and processes rows in batches to reduce I/O operations.
    """
    row_count = 0
    engine = init_db()
    session = Session(engine)

    try:
        with open(csv_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            required_headers = ["Ticker", "Date", "Time", "LTP", "BuyPrice", "BuyQty",
                                "SellPrice", "SellQty", "LTQ", "OpenInterest"]
            if not all(header in csv_reader.fieldnames for header in required_headers):
                return csv_path, 0, f"Error: CSV file {csv_path} does not have the required headers."

            print(f"\nProcessing CSV file: {csv_path}")

            # Pre-fetch all existing tickers from the Ticks table for quick lookup
            existing_tickers = {tick.ticker: tick.id for tick in session.query(Ticks.ticker, Ticks.id).all()}

            # Collect unique tickers from the CSV file
            unique_tickers = set()
            orders_data = []

            for row in csv_reader:
                ticker = row['Ticker'].replace('.NSE', '')
                timestamp = datetime.strptime(f"{row['Date']} {row['Time']}", "%d/%m/%Y %H:%M:%S")

                # Collect unique tickers
                if ticker not in existing_tickers:
                    unique_tickers.add(ticker)

                # Prepare Orders data
                orders_data.append({
                    'timestamp': timestamp,
                    'ltp': float(row['LTP']),
                    'buyprice': float(row['BuyPrice']),
                    'buyqty': int(row['BuyQty']),
                    'sellprice': float(row['SellPrice']),
                    'sellqty': int(row['SellQty']),
                    'ltq': int(row['LTQ']),
                    'openinterest': int(row['OpenInterest']),
                    'ticker': ticker,  # Temporarily store ticker to map to tick_id later
                })

                row_count += 1

            # Bulk insert unique tickers into Ticks table
            if unique_tickers:
                session.bulk_insert_mappings(Ticks, [{'ticker': ticker} for ticker in unique_tickers])
                session.commit()

                # Refresh existing_tickers with newly inserted tickers
                new_tickers = session.query(Ticks.ticker, Ticks.id).filter(Ticks.ticker.in_(unique_tickers)).all()
                existing_tickers.update({ticker.ticker: ticker.id for ticker in new_tickers})

            # Fetch all tickers with their IDs for mapping
            ticker_to_id = existing_tickers

            # Map ticker to tick_id in orders_data
            for order in orders_data:
                ticker = order.pop('ticker')
                order['tick_id'] = ticker_to_id[ticker]

            # Insert Orders in batches
            for i in range(0, len(orders_data), BATCH_SIZE):
                batch = orders_data[i:i + BATCH_SIZE]
                session.bulk_insert_mappings(Orders, batch)
                session.commit()
                print(f"Processed {min(i + BATCH_SIZE, len(orders_data))} rows from {csv_path}")

            # Update the latest_order_id in the Ticks table
            for ticker, tick_id in ticker_to_id.items():
                latest_order = session.query(Orders).filter_by(tick_id=tick_id).order_by(Orders.timestamp.desc()).first()
                if latest_order:
                    session.query(Ticks).filter_by(id=tick_id).update({'latest_order_id': latest_order.id})
                session.commit()

        return csv_path, row_count, None
    except Exception as e:
        session.rollback()
        return csv_path, 0, str(e)
    finally:
        session.close()

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
