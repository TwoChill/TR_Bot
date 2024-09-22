import asyncio
import os
from data_manager import DataManager

DEBUG = True  # Control debug mode; set to True for testing with print statements and plots.
TICKER = "BTC-USD"
INTERVALS = ['5m', '15m', '30m', '1h', '4h', '1d', '1wk']

# Initialize DataManager instance
dm = DataManager(TICKER)
dm.DEBUG = DEBUG  # Set debug mode

# Get initial historical data if the data folder is not present
if not os.path.exists(TICKER):
    if DEBUG:
        print(f"Creating directory for {TICKER}")

    # Create directory if it doesn't exist
    dm.create_directory()


# Start the asynchronous periodic update
asyncio.run(dm.start_auto_fetch_data())


# TODO: Asynchronously fetch new data when necessary
# - Implement asynchronous fetching for each timeframe using appropriate data_manager functions.
# - Set up asynchronous tasks to run periodically to check for and fetch new data.

# TODO: Cap Data Lookback for Each Timeframe
# - Define lookback periods for each timeframe to optimize performance:
#   - Weekly: Last 12 weeks
#   - Daily: Last 60 days
#   - 4H: Last 30 days
#   - 1H: Last 14 days
#   - 30M: Last 7 days
#   - 15M: Last 3 days
# - Implement logic to truncate data to these lookback periods.

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
