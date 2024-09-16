import asyncio
import yfinance as yf
import pandas as pd
import os
import glob
from datetime import datetime, timedelta

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

class DataManager:
    DEBUG = False

    def __init__(self, ticker, period):
        """
        Initializes the DataManager with a specific ticker and period.

        Args:
            ticker (str): The symbol of the financial instrument (e.g., "BTC-USD").
            period (str): The historical data period (e.g., "60d" for the last 60 days).
        """
        self.ticker = ticker.upper()
        self.period = period.lower()
        self.intervals = ['5m', '15m', '30m', '1h', '4h', '1d', '1wk']
        self.last_lines = {}  # Dictionary to store the last line of CSV data for each save moment

    def create_directory(self):
        """
        Creates a directory for the given ticker if it doesn't exist.
        """
        if not os.path.exists(self.ticker):
            if self.DEBUG:
                print(f"{CYAN}Creating directory for symbol: {self.ticker}{END}")
            os.makedirs(self.ticker)

    def fetch_new_data(self, symbol, period, intervals):
        """
        Fetches new historical data for each specified interval, removes any existing data file,
        and creates a new data file with the updated data.

        Args:
            symbol (str): The symbol of the financial instrument (e.g., "BTC-USD").
            period (str): The lookback period for historical data (e.g., "60d" for the last 60 days).
            intervals (list): List of data intervals (e.g., ['5m', '15m', '30m', '1h']).

        This method iterates through each interval, fetches the corresponding historical data,
        deletes any existing data file for that interval, and saves the new data to a new file.
        """
        for interval in intervals:
            if self.DEBUG:
                print(f"\n{CYAN}Fetching new data for {symbol} for period {period} with interval {interval}{END}")

            # Fetch new data from Yahoo Finance or aggregate for 4-hour data
            if interval != '4h':
                data = yf.download(symbol, period=period, interval=interval)
            else:
                data = self.update_4h_data_from_1h()

            # Check if data was fetched successfully
            if data is None or data.empty:
                if self.DEBUG:
                    print(f"{RED}No data fetched for {symbol} with interval {interval}. Skipping.{END}")
                continue

            if self.DEBUG:
                print(f"{GREEN}Data fetched {NEGATIVE}successfully{END}{GREEN} for {symbol} with {UNDERLINE}{len(data)} records{END}{GREEN}.{END}")

            # Define the filename for storing the data
            filename = os.path.join(symbol, f"{symbol}_{interval}.csv")

            # If file exists, remove it
            if os.path.exists(filename):
                os.remove(filename)
                if self.DEBUG:
                    print(f"{RED}Removed existing file: {filename}{END}")

            # Save the new data to a CSV file
            data.to_csv(filename)
            if self.DEBUG:
                print(f"{CYAN}{UNDERLINE}New data saved to file: {filename}{END}")

    async def start_auto_fetch_data(self):
        """
        Asynchronously runs the fetch_new_data function every 30 seconds.
        """
        while True:
            # Get the current time
            now = datetime.now()

            # Calculate the next 30-second interval time
            if now.second < 30:
                next_run_time = now.replace(second=30, microsecond=0)
            else:
                next_run_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)

            # Calculate the time to sleep until the next run time
            sleep_duration = (next_run_time - datetime.now()).total_seconds()
            if self.DEBUG:
                print(f"\nNext update scheduled at: {next_run_time}")

            # Wait until the next scheduled run time
            await asyncio.sleep(sleep_duration)

            # Run the fetch_new_data function
            self.fetch_new_data(self.ticker, self.period, self.intervals)

    def update_4h_data_from_1h(self):
        """
        Creates 4-hour aggregated data from 1-hour data files for the given ticker.

        This method looks for 1-hour data files, aggregates them into 4-hour intervals,
        and returns the resulting aggregated DataFrame.
        """
        if self.DEBUG:
            print(f"\n{PURPLE}Creating 4-hour data from 1-hour data for {self.ticker}{END}")
        matching_files_1h = glob.glob(os.path.join(self.ticker, f"*{self.ticker}_1h.csv"))

        if matching_files_1h:
            filename_1h = max(matching_files_1h, key=os.path.getmtime)
            data_1h = pd.read_csv(filename_1h, index_col=0, parse_dates=True)

            if data_1h.empty:
                if self.DEBUG:
                    print(f"{RED}No 1-hour data available for {self.ticker}. Cannot create 4-hour data.{END}")
                return None  # Return None if no data is available

            data_4h = data_1h.resample('4h').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            })

            if self.DEBUG:
                print(f"{GREEN}4-hour data created successfully from 1-hour data with {UNDERLINE}{len(data_4h)} records{END}{GREEN}.{END}")

            # Return the aggregated DataFrame
            return data_4h
        else:
            if self.DEBUG:
                print(f"{RED}No 1-hour data files found for {self.ticker}. Cannot create 4-hour data.{END}")
            return None  # Return None if no matching files are found

