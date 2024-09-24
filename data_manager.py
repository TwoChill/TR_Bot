import asyncio
import time

import yfinance as yf
import pandas as pd
import os
import glob
from datetime import datetime, timedelta
from constants import RED, GREEN, NEGATIVE, BOLD, UNDERLINE, END, main_DEBUG, auto_FETCH, LIGHT_RED, plot_DEBUG, TICKER, \
    INTERVALS
from Plot_Data import PlotManager


plm = PlotManager(TICKER, INTERVALS)

class DataManager:

    def __init__(self, ticker):
        """
        Initializes the DataManager with a specific ticker and period.

        Args:
            ticker (str): The symbol of the financial instrument (e.g., "BTC-USD").
        """
        self.ticker = ticker.upper()
        self.intervals = ['5m', '15m', '30m', '1h', '4h', '1d', '1wk']
        self.period_map = {
            '1wk': '15mo',  # Good
            '1d': '6mo',    # Good
            '1h': '2wk',    # Good
            '5m': '1d',     # Good
            '15m': '4d',    # Good
            '30m': '4d'     # Good
        }

    def create_directory(self):
        """
        Creates a directory for the given ticker if it doesn't exist.
        """
        if not os.path.exists(self.ticker):
            os.makedirs(self.ticker)

    async def periodic_fetch_data(self, symbol, intervals):
        """
        Fetches new historical data for each specified interval, removes any existing data file,
        and creates a new data file with the updated data.

        Args:
            symbol (str): The symbol of the financial instrument (e.g., "BTC-USD").
            period (str): The lookback period for historical data (e.g., "60d" for the last 60 days).
            intervals (list): List of data intervals (e.g., ['5m', '15m', '30m', '1h']).

        This method iterates through each interval, fetches the corresponding historical data,
        deletes any existing data file for that interval, and saves the new data to a new file.
        :param symbol:
        :param intervals:
        """

        print()
        for interval in intervals:
            if interval != '4h':
                fetch_period = self.period_map.get(interval)
                data = yf.download(symbol, period=fetch_period, interval=interval, progress=False)
                if main_DEBUG:
                    print(
                        f"{RED}{NEGATIVE}DEBUG{END} {GREEN}{BOLD}{NEGATIVE}{GREEN}{BOLD}{NEGATIVE}Success!{END}{GREEN} Fetched {symbol} {interval} data from Yahoo Finance.{END}")
            else:
                data = self.update_4h_data_from_1h()
                if main_DEBUG:
                    print(
                        f"{RED}{NEGATIVE}DEBUG{END} {GREEN}{BOLD}{NEGATIVE}{GREEN}{BOLD}{NEGATIVE}Success!{END}{GREEN} Fetched {symbol} {interval} data from Yahoo Finance.{END}")

            # Check if data was fetched successfully
            if data is None or data.empty:
                if main_DEBUG:
                    print(
                        f"{RED}{NEGATIVE}DEBUG{END} {RED}No data fetched for {symbol} with interval {interval}. Skipping.{END}")
                continue

            # Define the filename for storing the data
            filename = os.path.join(symbol, f"{symbol}_{interval}.csv")
            if os.path.exists(filename):
                os.remove(filename)

            data.to_csv(filename)
        print()
        # Calculate S en R levels
        if plot_DEBUG:
            if main_DEBUG:
                print(
                    f"{RED}{NEGATIVE}DEBUG{END} {GREEN}{BOLD}{NEGATIVE}Plotting data...{END}")

            plm.start_plotting()
        # sr_dm.recalculate_senr_levels(intervals)

    async def start_trading_bot(self):
        """
        Asynchronously runs the fetch_new_data function every 30 seconds.
        """
        while True:
            now = datetime.now()

            if now.second < 30:
                next_run_time = now.replace(second=30, microsecond=0)
            else:
                next_run_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)

            sleep_duration = (next_run_time - datetime.now()).total_seconds()

            if auto_FETCH:
                await asyncio.sleep(sleep_duration)

                # Fetch new data asynchronously for each interval using its specific period
                await self.periodic_fetch_data(self.ticker, self.intervals)
            else:
                print(f"{RED}{NEGATIVE}DEBUG{END} {LIGHT_RED}{BOLD}Skip Auto Fetch!\n{END}")
                await asyncio.sleep(10000)

    def update_4h_data_from_1h(self):
        """
        Creates 4-hour aggregated data from 1-hour data files for the given ticker.

        This method looks for 1-hour data files, aggregates them into 4-hour intervals,
        and returns the resulting aggregated DataFrame.
        """

        matching_files_1h = glob.glob(os.path.join(self.ticker, f"*{self.ticker}_1h.csv"))

        if matching_files_1h:
            filename_1h = max(matching_files_1h, key=os.path.getmtime)
            data_1h = pd.read_csv(filename_1h, index_col=0, parse_dates=True)

            if data_1h.empty:
                return None  # Return None if no data is available

            data_4h = data_1h.resample('4h').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            })

            # Return the aggregated DataFrame
            return data_4h
        else:
            if main_DEBUG:
                print(f"{RED}No 1-hour data files found for {self.ticker}. Cannot create 4-hour data.{END}")
            return None  # Return None if no matching files are found

    async def fetch_data_and_update_levels(self, symbol, period, intervals):
        """
        Asynchronously fetches new historical data for each interval and updates support and resistance.

        Args:
            symbol (str): The symbol of the financial instrument.
            period (str): The lookback period for historical data.
            intervals (list): List of data intervals.
        """
        for interval in intervals:
            # Fetch new data from Yahoo Finance or aggregate for 4-hour data
            fetch_period = self.period_map.get(interval, period)
            if interval != '4h':
                data = yf.download(symbol, period=fetch_period, interval=interval, progress=False)
            else:
                data = self.update_4h_data_from_1h()

            # Check if data was fetched successfully
            if data is None or data.empty:
                if main_DEBUG:
                    print(f"No data fetched for {symbol} with interval {interval}. Skipping.")
                continue

            if main_DEBUG:
                print(f"Data fetched successfully for {symbol} with {len(data)} records.")

            # Define the filename for storing the data
            filename = os.path.join(symbol, f"{symbol}_{interval}.csv")

            # If file exists, remove it
            if os.path.exists(filename):
                os.remove(filename)

            # Save the new data to a CSV file
            data.to_csv(filename)

            # Update support and resistance levels
            # sr_dm.update_support_resistance(interval, data)
