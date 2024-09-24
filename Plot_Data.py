import mplfinance as mpf
import pandas as pd
import os
from constants import plot_DEBUG, main_DEBUG


class PlotManager:
    def __init__(self, ticker, intervals):
        self.ticker = ticker
        self.intervals = intervals

    def load_data_for_interval(self, interval):
        """
        Loads the CSV data for the specified interval.

        Args:
            interval (str): The time interval (e.g., '1wk', '1d').

        Returns:
            pd.DataFrame: The data loaded from the corresponding CSV file.
        """
        folder_path = os.path.join(self.ticker)
        file_name = f"{self.ticker}_{interval}.csv"
        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            return pd.read_csv(file_path, index_col=0, parse_dates=True)
        else:
            if main_DEBUG:
                print(f"No data found for interval {interval}.")
            return None

    def plot_with_volume(self, data, interval):
        """
        Plots the candlestick chart with volume for the specified data.

        Args:
            data (pd.DataFrame): The data to plot.
            interval (str): The time interval (e.g., '1wk', '1d').
        """
        title = f"{self.ticker} {interval.upper()} Candlestick with Volume"
        mpf.plot(data, type='candle', volume=True, title=title, style='yahoo')

    def add_support_resistance(self, data, support_levels, resistance_levels):
        """
        Adds support and resistance lines to the chart based on the provided levels.

        Args:
            data (pd.DataFrame): The data to plot.
            support_levels (list): A list of support price levels.
            resistance_levels (list): A list of resistance price levels.

        Returns:
            list: List of mplfinance addplot objects for support/resistance levels.
        """
        add_plots = []

        # Adding support lines (green)
        for level in support_levels:
            add_plots.append(mpf.make_addplot([level] * len(data), color='green', linestyle='--'))

        # Adding resistance lines (red)
        for level in resistance_levels:
            add_plots.append(mpf.make_addplot([level] * len(data), color='red', linestyle='--'))

        return add_plots

    def plot_with_support_resistance(self, data, interval, support_levels, resistance_levels):
        """
        Plots the candlestick chart with volume and adds support and resistance lines.

        Args:
            data (pd.DataFrame): The data to plot.
            interval (str): The time interval (e.g., '1wk', '1d').
            support_levels (list): A list of support price levels.
            resistance_levels (list): A list of resistance price levels.
        """
        title = f"{self.ticker} {interval.upper()} Candlestick with Volume and S/R Levels"
        add_plots = self.add_support_resistance(data, support_levels, resistance_levels)
        mpf.plot(data, type='candle', volume=True, title=title, style='yahoo', addplot=add_plots)

    def start_plotting(self):
        """
        Starts the plotting process for all intervals if plot_DEBUG is enabled.
        """
        if plot_DEBUG:
            for interval in self.intervals:
                data = self.load_data_for_interval(interval)
                if data is not None:
                    # For now, plot only with volume. In the future, you can replace with plot_with_support_resistance.
                    self.plot_with_volume(data, interval)
        else:
            print("Plotting is disabled. Enable plot_DEBUG in constants to activate plotting.")
