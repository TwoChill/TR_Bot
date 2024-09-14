import yfinance as yf
import pandas as pd
import os
import glob
from datetime import datetime, timedelta

DEBUG = None  # Enables or disables print statements

# Color constants for console output
BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
NEGATIVE = "\033[7m"
CROSSED = "\033[9m"
END = "\033[0m"

def get_all_data(ticker, period):
    def load_csv_data(filename_pattern):
        if DEBUG:
            print(f"{YELLOW}Loading CSV data matching pattern: {filename_pattern}{END}")
        matching_files = glob.glob(filename_pattern)
        if matching_files:
            latest_file = max(matching_files, key=os.path.getctime)
            if DEBUG:
                print(f"{GREEN}Latest file found: {latest_file}{END}")
            return pd.read_csv(latest_file, index_col=0, parse_dates=True)
        else:
            if DEBUG:
                print(f"{RED}No matching files found for pattern: {filename_pattern}{END}")
            return pd.DataFrame()

    def fetch_new_data(symbol, period, interval):
        if DEBUG:
            print(f"{CYAN}Fetching new data for {symbol} for period {period} with interval {interval}{END}")
        data = yf.download(symbol, period=period, interval=interval)
        if DEBUG:
            print(f"{GREEN}Data fetched successfully for {symbol} with {len(data)} records.{END}")
        return data

    def is_update_needed(filename, interval):
        if DEBUG:
            print(f"{BLUE}Checking if update is needed for file: {filename} with interval: {interval}{END}")
        base, _ = os.path.splitext(filename)
        parts = base.split('_')

        if len(parts) > 2:
            try:
                if interval in ['5m', '15m', '30m']:
                    date_str, time_str = parts[-2], parts[-1]
                    file_time = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y__%H.%M")
                elif interval in ['1h', '4h']:
                    date_str, hour_str = parts[-2].strip(), parts[-1].strip()
                    file_time = datetime.strptime(f"{date_str} {hour_str}", "%d.%m.%Y__%H")
                else:
                    date_str = parts[-1]
                    file_time = datetime.strptime(date_str, "%d.%m.%Y")

                current_time = datetime.now()
                delta = {
                    '5m': timedelta(minutes=5),
                    '15m': timedelta(minutes=15),
                    '30m': timedelta(minutes=30),
                    '1h': timedelta(hours=1),
                    '4h': timedelta(hours=4),
                    '1d': timedelta(days=1),
                    '1wk': timedelta(weeks=1)
                }.get(interval, timedelta(days=1))

                update_needed = current_time > file_time + delta
                if DEBUG:
                    print(f"{GREEN}Update needed: {update_needed}{END}")
                return update_needed
            except ValueError:
                if DEBUG:
                    print(f"{RED}Warning: Invalid date format in filename {filename}. Assuming update is needed.{END}")
                return True
        return True

    def update_csv_data(symbol, period, interval):
        if DEBUG:
            print(f"\n{PURPLE}Updating CSV data for {symbol} with interval {interval}{END}")
        if not os.path.exists(symbol):
            os.makedirs(symbol)
            if DEBUG:
                print(f"{GREEN}Created directory for symbol: {symbol}{END}")

        filename = os.path.join(symbol, f"{symbol}_{interval}.csv")

        if not os.path.exists(filename) or is_update_needed(filename, interval):
            new_data = fetch_new_data(symbol, period, interval)
            existing_data = load_csv_data(filename)

            if not existing_data.empty:
                combined_data = pd.concat([existing_data, new_data])
                combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
                if DEBUG:
                    print(f"{CYAN}Combined existing and new data. Total records: {len(combined_data)}{END}")
            else:
                combined_data = new_data
                if DEBUG:
                    print(f"{CYAN}No existing data. Using new data only.{END}")

            combined_data.to_csv(filename)
            rename_csv_with_date(filename, interval)
        else:
            if DEBUG:
                print(f"{YELLOW}No update needed for {filename}{END}")

    def rename_csv_with_date(filename, interval):
        if DEBUG:
            print(f"{BLUE}Renaming CSV file based on interval: {interval}{END}")
        base, ext = os.path.splitext(filename)
        date_str = {
            '5m': datetime.now().strftime('%d.%m.%Y__%H.%M'),
            '15m': datetime.now().strftime('%d.%m.%Y__%H.%M'),
            '30m': datetime.now().strftime('%d.%m.%Y__%H.%M'),
            '1h': datetime.now().strftime('%d.%m.%Y__%H'),
            '4h': datetime.now().strftime('%d.%m.%Y__%H'),
        }.get(interval, datetime.now().strftime('%d.%m.%Y'))

        new_filename = f"{base}_{date_str}{ext}"
        if os.path.exists(new_filename):
            if DEBUG:
                print(f"{RED}File {new_filename} already exists, no renaming needed.{END}")
        elif os.path.exists(filename):
            os.rename(filename, new_filename)
            if DEBUG:
                print(f"{GREEN}Renamed file to {new_filename}{END}")
        else:
            if DEBUG:
                print(f"{RED}File {filename} does not exist to rename.{END}")

    def update_4h_data_from_1h(symbol):
        if DEBUG:
            print(f"\n{PURPLE}Creating 4-hour data from 1-hour data for {symbol}{END}")
        matching_files_1h = glob.glob(os.path.join(symbol, f"*{symbol}_1h*.csv"))

        if matching_files_1h:
            filename_1h = max(matching_files_1h, key=os.path.getmtime)
            data_1h = load_csv_data(filename_1h)

            if data_1h.empty:
                if DEBUG:
                    print(f"{RED}No 1-hour data available for {symbol}. Cannot create 4-hour data.{END}")
                return

            data_4h = data_1h.resample('4h').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            })

            filename_4h = os.path.join(symbol, f"{symbol}_4h.csv")
            data_4h.to_csv(filename_4h)

            rename_csv_with_date(filename_4h, '4h')
        else:
            if DEBUG:
                print(f"{RED}No 1-hour data files found for {symbol}. Cannot create 4-hour data.{END}")

    def remove_unnecessary_files(symbol):
        if DEBUG:
            print(f"{CYAN}Removing unnecessary files for symbol: {symbol}{END}")
        valid_patterns = [
            os.path.join(symbol, f"{symbol}_5m_*.csv"), os.path.join(symbol, f"{symbol}_15m_*.csv"),
            os.path.join(symbol, f"{symbol}_30m_*.csv"), os.path.join(symbol, f"{symbol}_1h_*.csv"),
            os.path.join(symbol, f"{symbol}_4h_*.csv"), os.path.join(symbol, f"{symbol}_1d_*.csv"),
            os.path.join(symbol, f"{symbol}_1wk_*.csv")
        ]

        all_files = glob.glob(os.path.join(symbol, f"{symbol}_*.csv"))

        files_to_keep = []
        for pattern in valid_patterns:
            files_to_keep.extend(glob.glob(pattern))

        for file in all_files:
            if file not in files_to_keep:
                os.remove(file)
                if DEBUG:
                    print(f"{RED}Removed file: {file}{END}")

    ticker = ticker.upper()
    period = period.lower()
    intervals = ['5m', '15m', '30m', '1h', '1d', '1wk']

    if os.path.exists(ticker):
        if DEBUG:
            print(f"{RED}Removing directory for symbol: {ticker} and refetching all files...{END}")
        for root, dirs, files in os.walk(ticker, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(ticker)

    if DEBUG:
        print(f"\n{NEGATIVE}{LIGHT_RED}Updating data for {LIGHT_RED}{NEGATIVE} {ticker}...{END}\n")
    for interval in intervals:
        update_csv_data(ticker, period, interval)

    update_4h_data_from_1h(ticker)

    remove_unnecessary_files(ticker)
