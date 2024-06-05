import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

# 读取数据
file_path = r'C:\\Users\\zrhe2\\Desktop\\BTCUSDT_1m_2018-2024.csv'
df = pd.read_csv(file_path)

# 将时间戳转换为日期时间格式
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# 设定时间列为索引
df.set_index('timestamp', inplace=True)

# 自定义选取数据的时间范围
start_date = '2018-01-01'  # 设置起始日期
end_date = '2024-01-01'    # 设置结束日期
df_selected = df.loc[start_date:end_date]

# 定义计算随机指标的函数


def calculate_stoch(df, k, d):
    lowest_low = df['low'].rolling(window=k).min()
    highest_high = df['high'].rolling(window=k).max()
    lowest_close = df['close'].rolling(window=k).min()
    highest_close = df['close'].rolling(window=k).max()

    # 防止分母为零的情况
    denom = highest_close - lowest_close
    denom[denom == 0] = 1  # 处理分母为零的情况

    nk1 = ta.SMA((df['close'] - lowest_close) / denom * 100, d)
    nd1 = ta.SMA(nk1, d)
    return nk1, nd1

# 定义一个函数来计算并比较不同时间框架的指标


def compare_stoch_indicators(df, tf1, tf2, k1, d1, k_range, d_range):
    # 在tf1时间框架计算随机指标
    df_tf1 = df.resample(tf1).agg(
        {'close': 'last', 'high': 'max', 'low': 'min'}).dropna()
    df_tf1['nk1'], df_tf1['nd1'] = calculate_stoch(df_tf1, k1, d1)

    # 将tf1的计算结果填充到tf2框架
    df_tf2 = df.resample(tf2).agg(
        {'close': 'last', 'high': 'max', 'low': 'min'}).dropna()
    df_tf2 = df_tf2.join(df_tf1[['nk1', 'nd1']]).ffill()

    # 预先计算指标并缓存结果
    stoch_cache = {}
    for k in k_range:
        for d in d_range:
            stoch_cache[(k, d)] = calculate_stoch(df_tf2, k, d)

    # 在tf2框架计算第二个指标，尝试多个参数
    best_k = None
    best_d = None
    best_mse = float('inf')

    # 遍历缓存的结果
    for (k, d), (nk1_tf2, nd1_tf2) in stoch_cache.items():
        common_index = df_tf2.dropna(
            subset=['nd1']).index.intersection(nd1_tf2.dropna().index)
        if common_index.empty:
            continue
        aligned_nd1 = df_tf2.loc[common_index, 'nd1']
        aligned_nd1_tf2 = nd1_tf2.loc[common_index]
        mse = mean_squared_error(aligned_nd1, aligned_nd1_tf2)
        if mse < best_mse:
            best_mse = mse
            best_k = k
            best_d = d

    if best_k is None or best_d is None:
        print("未找到合适的参数。")
        return

    print(f"最相似的参数是: k = {best_k}, d = {best_d}")

    # 绘制结果对比
    df_tf2['best_nk1'], df_tf2['best_nd1'] = stoch_cache[(best_k, best_d)]
    plt.figure(figsize=(14, 7))
    plt.plot(df_tf2.index, df_tf2['nd1'], label=f'{tf1} nd1')
    plt.plot(df_tf2.index, df_tf2['best_nd1'], label=f'{
             tf2} nd1 (k={best_k}, d={best_d})')
    plt.legend()
    plt.show()


# 定义时间框架和参数
time_frame_1 = '2H'  # 第一个时间框架
time_frame_2 = '30T'  # 第二个时间框架
k1 = 30  # 第一个时间框架的k值
d1 = 9   # 第一个时间框架的d值
k_range = range(30, 201)  # 第二个时间框架k值的范围
d_range = range(6, 61)    # 第二个时间框架d值的范围

# 比较不同时间框架的指标
compare_stoch_indicators(df_selected, time_frame_1,
                         time_frame_2, k1, d1, k_range, d_range)
