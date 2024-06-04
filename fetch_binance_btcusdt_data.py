import ccxt
import pandas as pd
from datetime import datetime, timedelta

# 初始化币安交易所
exchange = ccxt.binance()

# 定义时间范围和时间间隔
symbol = 'BTC/USDT'
since = exchange.parse8601('2018-01-01T00:00:00Z')
end_time = exchange.parse8601('2024-01-01T00:00:00Z')
timeframe = '30m'

# 函数：获取历史数据


def fetch_ohlcv_data(exchange, symbol, timeframe, since, end_time):
    all_ohlcv = []
    while since < end_time:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=500)
        if not ohlcv:
            break
        since = ohlcv[-1][0] + exchange.parse_timeframe(timeframe) * 1000
        all_ohlcv += ohlcv
        print(f"Fetched {len(ohlcv)} records from {exchange.iso8601(
            ohlcv[0][0])} to {exchange.iso8601(ohlcv[-1][0])}")
    return all_ohlcv


# 获取数据
ohlcv_data = fetch_ohlcv_data(exchange, symbol, timeframe, since, end_time)

# 将数据转换为 DataFrame
df = pd.DataFrame(ohlcv_data, columns=[
                  'timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# 保存数据到 CSV 文件
df.to_csv('BTCUSDT_30m_2018-2024.csv', index=False)

print("数据已保存到 BTCUSDT_30m_2018-2024.csv")
