# TODO 1: Markup Charts

# TODO 1.1: Fetch Timeframe Data
# TODO 1.1.1: Rename Timeframe CSV and Update Data
# - Load data from the CSV file for each timeframe.
# - Ensure the CSV filenames are descriptive (e.g., "BTCUSD_15min.csv").
# - Implement a function to fetch new data, update, and rename the CSV files with the latest data.

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
