# TODO 1: Markup Charts
import time

import yfinance as yf
import pandas as pd
import os
import glob
from datetime import datetime, timedelta


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

def load_csv_data(filename_pattern):
    matching_files = glob.glob(filename_pattern)
    if matching_files:
        latest_file = max(matching_files, key=os.path.getctime)
        return pd.read_csv(latest_file, index_col=0, parse_dates=True)
    else:
        return pd.DataFrame()


def fetch_new_data(symbol, period, interval):
    data = yf.download(symbol, period=period, interval=interval)
    return data


def is_update_needed(filename, interval):
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

            if interval == '5m':
                delta = timedelta(minutes=5)
            elif interval == '15m':
                delta = timedelta(minutes=15)
            elif interval == '30m':
                delta = timedelta(minutes=30)
            elif interval == '1h':
                delta = timedelta(hours=1)
            elif interval == '4h':
                delta = timedelta(hours=4)
            elif interval == '1d':
                delta = timedelta(days=1)
            elif interval == '1wk':
                delta = timedelta(weeks=1)

            return current_time > file_time + delta
        except ValueError:
            print(f"Warning: Invalid date format in filename {filename}. Assuming update is needed.")
            return True

    return True


def update_csv_data(symbol, period, interval):
    filename = f"{symbol}_{interval}.csv"

    if not os.path.exists(filename) or is_update_needed(filename, interval):
        new_data = fetch_new_data(symbol, period, interval)

        existing_data = load_csv_data(filename)
        if not existing_data.empty:
            combined_data = pd.concat([existing_data, new_data])
            combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
        else:
            combined_data = new_data

        combined_data.to_csv(filename)

        rename_csv_with_date(filename, interval)
    else:
        print(f"No update needed for {filename}")


def rename_csv_with_date(filename, interval):
    base, ext = os.path.splitext(filename)
    if interval in ['5m', '15m', '30m']:
        new_filename = f"{base}_{datetime.now().strftime('%d.%m.%Y__%H.%M')}{ext}"
    elif interval in ['1h', '4h']:
        new_filename = f"{base}_{datetime.now().strftime('%d.%m.%Y__%H')}{ext}"
    else:
        new_filename = f"{base}_{datetime.now().strftime('%d.%m.%Y')}{ext}"

    #
    if os.path.exists(new_filename):
        pass
    elif os.path.exists(filename):
        os.rename(filename, new_filename)
    else:
        print(f"File {filename} does not exist to rename.")


def update_4h_data_from_1h(symbol):
    matching_files_1h = glob.glob(f"*{symbol}_1h*.csv")

    if matching_files_1h:
        filename_1h = max(matching_files_1h, key=os.path.getmtime)
        data_1h = load_csv_data(filename_1h)

        if data_1h.empty:
            print(f"No 1-hour data available for {symbol}. Cannot create 4-hour data.")
            return

        data_4h = data_1h.resample('4h').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })

        filename_4h = f"{symbol}_4h.csv"
        data_4h.to_csv(filename_4h)

        rename_csv_with_date(filename_4h, '4h')
    else:
        print(f"No 1-hour data files found for {symbol}. Cannot create 4-hour data.")


def remove_unnecessary_files(symbol):
    """
    Remove unnecessary files that do not match the correct naming pattern.

    Parameters:
    symbol (str): The stock or cryptocurrency symbol to process.
    """
    # Define correct patterns to keep
    valid_patterns = [
        f"{symbol}_5m_*.csv", f"{symbol}_15m_*.csv", f"{symbol}_30m_*.csv",
        f"{symbol}_1h_*.csv", f"{symbol}_4h_*.csv", f"{symbol}_1d_*.csv", f"{symbol}_1wk_*.csv"
    ]

    # Collect all files related to the symbol
    all_files = glob.glob(f"{symbol}_*.csv")

    # Determine files to keep
    files_to_keep = []
    for pattern in valid_patterns:
        files_to_keep.extend(glob.glob(pattern))

    # Remove files not matching the correct patterns
    for file in all_files:
        if file not in files_to_keep:
            os.remove(file)


symbol = 'BTC-USD'
period = '60d'
intervals = ['5m', '15m', '30m', '1h', '1d', '1wk']

print(f"\n{NEGATIVE}{LIGHT_RED}Updating data for {LIGHT_RED}{NEGATIVE} {symbol}...{END}\n")
for interval in intervals:
    update_csv_data(symbol, period, interval)

print(f"\n{NEGATIVE}{LIGHT_GREEN}Updating completed.{END}")
time.sleep(2)

update_4h_data_from_1h(symbol)


# Remove unnecessary files after updates
remove_unnecessary_files(symbol)

# TODO 1.1.2: Cap Data Lookback for Each Timeframe
# - Limit the lookback period for each timeframe to manage performance and data size.
# - Define specific lookback periods for each timeframe:
#   - Weekly: Last 12 weeks
#   - Daily: Last 60 days
#   - 4H: Last 30 days
#   - 1H: Last 14 days
#   - 30M: Last 7 days
#   - 15M: Last 3 days

# TODO 1.2: Plot Recent Support and Resistance Levels on Each Timeframe
# TODO 1.2.1: Show Metaplots and Add Variables for Resistance and Support if Debug is Set to True
# - Plot support and resistance levels on each timeframe.
# - Enable metaplots for debugging purposes by setting debug to True.
debug = True  # Enable/Disable debugging visualization

# Initialize variables for support and resistance levels on each timeframe.
recent_weekly_resistance = int()
recent_weekly_support = int()
recent_daily_resistance = int()
recent_daily_support = int()
recent_4h_resistance = int()
recent_4h_support = int()
recent_1h_resistance = int()
recent_1h_support = int()
recent_30m_resistance = int()
recent_30m_support = int()
recent_15m_resistance = int()
recent_15m_support = int()

# TODO 1.2.2: Add New Support and Resistance Levels for Each Timeframe
# - Calculate new support and resistance levels after data updates.
# - Update each timeframe with new support and resistance levels based on recent data.

# TODO 1.2.3: Determine Minimal Trading Range
# - Calculate the minimal trading range required for effective trading on each timeframe.
# - Use the latest support and resistance levels to define the range.

# TODO 1.2.4: Refresh TimeFrame Data Based on Their Timeframes
# - Implement a function to refresh the data periodically based on the timeframe.
# - Check if new data has been added since the last refresh and update the dataset accordingly.

# TODO 1.2.5: Check Each Refresh for New Recent Support and Resistance Levels
# - Recalculate support and resistance levels after each data refresh.
# - Update the support and resistance variables for each timeframe with the latest values.

# TODO 1.3: Validate and Clean Data
# TODO 1.3.1: Check for Missing Values
# - Implement data validation to identify missing values.
# - Decide whether to fill missing values (e.g., using interpolation) or remove the affected data points.

# TODO 1.3.2: Remove Outliers
# - Detect and remove outliers in the dataset that may affect analysis.
# - Use statistical methods such as Z-score or Interquartile Range (IQR) to identify outliers.
# - Decide whether to remove or adjust outliers based on the trading strategy.
