import ccxt
import pandas as pd
import logging
from datetime import datetime

# Initialize Binance exchange
exchange = ccxt.binance()

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define time range and interval
symbol = 'BTC/USDT'
since = exchange.parse8601('2018-01-01T00:00:00Z')
end_time = exchange.parse8601('2024-01-01T00:00:00Z')
timeframe = '1m'

# Function to fetch historical data


def fetch_ohlcv_data(exchange, symbol, timeframe, since, end_time):
    all_ohlcv = []
    while since < end_time:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=500)
            if not ohlcv:
                break
            since = ohlcv[-1][0] + exchange.parse_timeframe(timeframe) * 1000
            all_ohlcv += ohlcv
            logging.info(f"Fetched {len(ohlcv)} records from {
                         exchange.iso8601(ohlcv[0][0])} to {exchange.iso8601(ohlcv[-1][0])}")
        except ccxt.NetworkError as e:
            logging.warning(f'NetworkError: {str(e)}. Retrying...')
            continue
        except ccxt.ExchangeError as e:
            logging.error(f'ExchangeError: {str(e)}')
            break
    return all_ohlcv


# Fetch data
ohlcv_data = fetch_ohlcv_data(exchange, symbol, timeframe, since, end_time)

# Keep only the first five columns (timestamp, open, high, low, close)
ohlcv_data = [item[:5] for item in ohlcv_data]

# Convert data to DataFrame
df = pd.DataFrame(ohlcv_data, columns=[
                  'timestamp', 'open', 'high', 'low', 'close'])

# Save data to CSV file
df.to_csv('BTCUSDT_1m_2018-2024.csv', index=False)
logging.info("Data has been saved to BTCUSDT_1m_2018-2024.csv")
