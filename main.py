import asyncio
import os
from data_manager import DataManager
from constants import auto_FETCH, main_DEBUG, RED, NEGATIVE, END, GREEN, BOLD, LIGHT_RED, PURPLE

TICKER = "BTC-USD"
INTERVALS = ['5m', '15m', '30m', '1h', '4h', '1d', '1wk']

# Initialize DataManager instance
dm = DataManager(TICKER)

# Get initial historical data if the data folder is not present
try:
    if not os.path.exists(TICKER):
        if main_DEBUG:
            print(f"Creating directory for {TICKER}")

        # Create directory if it doesn't exist
        dm.create_directory()

    if auto_FETCH:
        if main_DEBUG:
            print(
                f"{RED}{NEGATIVE}DEBUG{END} {GREEN}{BOLD}{NEGATIVE}{GREEN}{BOLD}{NEGATIVE}Fetching Data...{END}")
        else:
            print(
                f"{PURPLE}{BOLD}{NEGATIVE}{NEGATIVE}Running...{END}")

    # Start the asynchronous periodic update
    asyncio.run(dm.start_trading_bot())

# Catch user interrupts
except KeyboardInterrupt:
    if main_DEBUG:
        print(f"\n{RED}{NEGATIVE}DEBUG{END} {RED}{BOLD}{NEGATIVE}Exiting...{END}")
    else:
        print(
            f"\n{RED}{BOLD}{NEGATIVE}{NEGATIVE}Exiting...{END}")
except Exception as e:
    if main_DEBUG:
        print(f"\n{RED}{NEGATIVE}DEBUG{END} {RED}{BOLD}{NEGATIVE}Error:{END} {RED}{e}{END}")
    else:
        print(
            f"\n{RED}{BOLD}{NEGATIVE}Error:{END} {RED}{e}{END}")

# TODO: Plot Recent Support and Resistance Levels on Each Timeframe
# - Develop a plotting function to visualize support and resistance levels for each timeframe.
# - Use `matplotlib` or another visualization library to generate these plots.

# TODO: Show Metaplots and Add Variables for Resistance and Support if Debug is Set to True
# - Create a meta-plot function to overlay multiple plots for debugging.
# - Conditionally display these plots only when DEBUG is set to True.

# Initialize variables for support and resistance levels on each timeframe.
# recent_weekly_resistance = int()
# recent_weekly_support = int()
# recent_daily_resistance = int()
# recent_daily_support = int()
# recent_4h_resistance = int()
# recent_4h_support = int()
# recent_1h_resistance = int()
# recent_1h_support = int()
# recent_30m_resistance = int()
# recent_30m_support = int()
# recent_15m_resistance = int()
# recent_15m_support = int()

# TODO: Add New Support and Resistance Levels for Each Timeframe
# - Calculate new support and resistance levels using recent data points.
# - Update the initialized variables accordingly after data updates.

# TODO: Determine Minimal Trading Range
# - Define the minimal trading range for each timeframe.
# - Use current support and resistance levels to calculate the range.

# TODO: Refresh TimeFrame Data Based on Their Timeframes
# - Implement a periodic refresh function for each timeframe.
# - Check timestamps to determine if new data is available since the last refresh.

# TODO: Check Each Refresh for New Recent Support and Resistance Levels
# - After each data refresh, recalculate support and resistance levels.
# - Update the relevant variables to reflect the latest values.

# TODO: Validate and Clean Data
# - Create a data validation function to check for missing or erroneous values.
# - Decide whether to interpolate missing values or drop affected rows.

# TODO: Remove Outliers
# - Implement outlier detection using statistical methods (e.g., Z-score, IQR).
# - Apply a strategy for handling outliers (removal or adjustment) based on the trading strategy.
