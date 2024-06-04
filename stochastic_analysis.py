import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

# 读取数据
file_path = r'C:\Users\zrhe2\Desktop\BTC_USDT_30m_2023-2024.csv'
df = pd.read_csv(file_path, parse_dates=['date'])

# 设定时间列为索引
df.set_index('date', inplace=True)

# 随机选取7天数据
start_date = df.index.min()
end_date = start_date + pd.Timedelta(days=60)
df_7days = df.loc[start_date:end_date]

# 定义计算随机指标的函数


def calculate_stoch(df, k, d):
    low = df['close'].rolling(window=k).min()
    high = df['close'].rolling(window=k).max()
    nk1 = ta.SMA((df['close'] - low) / (high - low) * 100, d)
    nd1 = ta.SMA(nk1, d)
    return nk1, nd1


# 在2小时框架计算随机指标
df_2h = df_7days.resample('2H').agg({'close': 'last'}).dropna()
df_2h['nk1'], df_2h['nd1'] = calculate_stoch(df_2h, 30, 9)

# 将2小时的计算结果填充到30分钟框架
df_30m = df_7days.resample('30T').agg({'close': 'last'}).dropna()
df_30m = df_30m.join(df_2h[['nk1', 'nd1']]).ffill()

# 在30分钟框架计算第二个指标，尝试多个参数
best_k = None
best_d = None
best_mse = float('inf')

for k in range(30, 201):
    for d in range(6, 61):
        nk1_30m, nd1_30m = calculate_stoch(df_30m, k, d)

        # 对齐索引，确保两个序列的长度一致
        common_index = df_30m.dropna(
            subset=['nd1']).index.intersection(nd1_30m.dropna().index)
        aligned_nd1 = df_30m.loc[common_index, 'nd1']
        aligned_nd1_30m = nd1_30m.loc[common_index]

        mse = mean_squared_error(aligned_nd1, aligned_nd1_30m)

        if mse < best_mse:
            best_mse = mse
            best_k = k
            best_d = d

print(f"最相似的参数是: k = {best_k}, d = {best_d}")

# 绘制结果对比
df_30m['best_nk1'], df_30m['best_nd1'] = calculate_stoch(
    df_30m, best_k, best_d)

plt.figure(figsize=(14, 7))
plt.plot(df_30m.index, df_30m['nd1'], label='2H nd1')
plt.plot(df_30m.index, df_30m['best_nd1'],
         label=f'30M nd1 (k={best_k}, d={best_d})')
plt.legend()
plt.show()
