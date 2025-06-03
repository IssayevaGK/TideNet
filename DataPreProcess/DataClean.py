import os
import pandas as pd
import numpy as np
from math import sqrt
from collections import Counter
from datetime import datetime

# 相似判定中的分组mmsi数量
mmsi_count_has_sim = 0
mmsi_count = 0

# 文件夹路径
input_folder = 'D:/gohak/data/AIS/clean/'
output_folder = input_folder + 'HasCleaned'

# 如果输出文件夹不存在，则创建它
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 通过经纬度计算出连续两点间的实际距离𝐷𝑖𝑠
def calculate_distance(data):
    x1 = np.radians(data['LAT'].shift(1))
    y1 = np.radians(data['LON'].shift(1))
    x2 = np.radians(data['LAT'])
    y2 = np.radians(data['LON'])
    earth_r = 6371.393
    d = (np.sin(((x2 - x1) / 2))) ** 2 + np.cos(x1) * np.cos(x2) * ((np.sin(((y2 - y1) / 2))) ** 2)
    distance = 2000 * earth_r * np.arcsin(np.sqrt(d))

    time = pd.to_datetime(data['BaseDateTime'], format='%Y-%m-%dT%H:%M:%S').diff().dt.total_seconds()
    max_distance = time * 51.2 * 1852 / 3600

    data['Distance'] = distance.fillna(0)
    data['MaxDistance'] = max_distance.fillna(0)

    return data

# 数值型数据的相似判断
def similar_number(num1, num2):
    if pd.isna(num1) and pd.isna(num2):
        return 1
    if pd.isna(num1) or pd.isna(num2):
        return 0
    if max(num1, num2) == 0:
        return 1 if num1 == num2 else 0
    sim = 1 - abs((num1 - num2) / max(num1, num2))
    return sim

# 字符型数据的相似判断
def similar_string(str1, str2):
    if pd.isna(str1) and pd.isna(str2):
        return 1
    if pd.isna(str1) or pd.isna(str2):
        return 0
    vector1 = Counter(list(str1))
    vector2 = Counter(list(str2))

    shared = set(vector1.keys()) & set(vector2.keys())
    numerator = sum([vector1[x] * vector2[x] for x in shared])

    sum1 = sum([vector1[x] ** 2 for x in vector1.keys()])
    sum2 = sum([vector2[x] ** 2 for x in vector2.keys()])
    denominator = sqrt(sum1 * sum2)

    return float(numerator) / denominator if denominator else 0.0

# 布尔型数据的相似判断
def similar_bool(bool1, bool2):
    if pd.isna(bool1) and pd.isna(bool2):
        return 1
    if pd.isna(bool1) or pd.isna(bool2):
        return 0
    return bool1 == bool2

# 数据的相似判断
def similar(wei, row1, row2):
    sim_time = similar_string(row1['BaseDateTime'], row2['BaseDateTime'])
    sim_lat = similar_number(row1['LAT'], row2['LAT'])
    sim_lon = similar_number(row1['LON'], row2['LON'])
    sim_sog = similar_number(row1['SOG'], row2['SOG'])
    sim_cog = similar_number(row1['COG'], row2['COG'])
    sim_heading = similar_number(row1['Heading'], row2['Heading'])
    sim_vessel_name = similar_string(row1['VesselName'], row2['VesselName'])
    sim_imo = similar_string(row1['IMO'], row2['IMO'])
    sim_call_sign = similar_string(row1['CallSign'], row2['CallSign'])
    sim_vessel_type = similar_number(row1['VesselType'], row2['VesselType'])
    sim_status = similar_number(row1['Status'], row2['Status'])
    sim_length = similar_number(row1['Length'], row2['Length'])
    sim_width = similar_number(row1['Width'], row2['Width'])
    sim_draft = similar_number(row1['Draft'], row2['Draft'])
    sim_cargo = similar_number(row1['Cargo'], row2['Cargo'])
    sim_transceiver_class = similar_bool(row1['TransceiverClass'], row2['TransceiverClass'])
    sim = np.array([sim_time, sim_lat, sim_lon, sim_sog, sim_cog, sim_heading, sim_vessel_name, sim_imo, sim_call_sign,
                    sim_vessel_type, sim_status, sim_length, sim_width, sim_draft, sim_cargo, sim_transceiver_class])
    wei_sim = np.sum(sim * wei)
    return wei_sim > 0.95

# 改进的动态滑动窗口策略
def dynamic_window(data, wei, initial_window_size, threshold):
    global mmsi_count_has_sim, mmsi_count
    mmsi_count_has_sim += 1
    print(f"\n{mmsi_count_has_sim}/{mmsi_count}")
    window_size = initial_window_size
    counter = 0
    repetition_number = []
    for begin in range(0, len(data)):
        if begin in repetition_number:
            continue
        compared = 0
        window_begin = begin
        now = window_begin + 1
        while compared < window_size:
            if now >= len(data):
                break
            if similar(wei, data.iloc[window_begin], data.iloc[now]):
                window_change = window_size - 1
                window_size = now - window_begin + 1 + window_change
                repetition_number.append(now)
                data.loc[data.index[now], 'ISSIMILAR'] = 1
            else:
                counter += 1
                if counter > threshold:
                    window_change = window_size - counter - 1
                    window_size = now - window_begin + 1 - window_change
                    counter = 0
                    break
            compared += 1
            now += 1
    return data

# 遍历文件夹中的所有CSV文件
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        file_path = os.path.join(input_folder, filename)

        # 相似判定中的分组mmsi数量
        mmsi_count_has_sim = 0

        # Load the dataset
        print("read open\n")
        #df = pd.read_csv(file_path, dtype={8: str})
        df = pd.read_csv(file_path, dtype={
            "MMSI": str,
            "BaseDateTime": str,
            "LAT": float,
            "LON": float,
            "SOG": float,
            "COG": float,
            "Heading": float,
            "VesselName": str,
            "IMO": str,
            "CallSign": str,
            "VesselType": float,
            "Status": float,
            "Length": float,
            "Width": float,
            "Draft": float,
            "Cargo": float,
            "TransceiverClass": str
        }, low_memory=False)
        print("read end\n")

        # 1. 将 AIS 数据按 MMSI 和时间升幂排序
        df.sort_values(by=['MMSI', 'BaseDateTime'], inplace=True)
        print("1 Sort AIS data by MMSI and time ascension end\n")

        # 2. 删除 MMSI 不为 9 位的数据
        #df = df[df['MMSI'].apply(lambda x: len(str(x)) == 9)]
        df = df[df['MMSI'].str.len() == 9]
        print("2 Delete data whose MMSI is not 9 bits end\n")

        # 3. 删除MMSI相同、IMO不同的情况，一般为套牌船
        df = df.groupby('MMSI').filter(lambda x: x['IMO'].nunique() <= 1).reset_index(drop=True)
        print("3 Deletion of the same MMSI and different IMO is generally a set ship end\n")

        # 4. 删除一个月内的AIS数据不足1000条的轨迹
        df = df.groupby('MMSI').filter(lambda x: x['MMSI'].count() > 1000).reset_index(drop=True)
        print("4 Deletion of trajectories with less than 1000 AIS data in one month end\n")

        # 5. 删除船长小于 3 和船宽小于 2 的船舶数据
        df = df[(df['Length'] >= 3) & (df['Width'] >= 2)].reset_index(drop=True)
        print("5 Deletion of data for vessels less than 3 in length and 2 in breadth end\n")

        # Ensure numeric types for relevant columns, including 'Draft'
        columns_to_convert = ['SOG', 'COG', 'LON', 'LAT', 'Length', 'Width', 'Draft']
        for column in columns_to_convert:
            df[column] = pd.to_numeric(df[column], errors='coerce')

        # 6. 删除超出有效范围的经度、维度、对地航速、对地航向数据
        df = df[(df['LON'] >= -180.0) & (df['LON'] <= 180.0)]
        df = df[(df['LAT'] >= -90.0) & (df['LAT'] <= 90.0)]
        df = df[(df['SOG'] >= 0) & (df['SOG'] <= 102.4)]
        df = df[(df['COG'] >= 0) & (df['COG'] <= 360)].reset_index(drop=True)
        print("6 Deletion of longitude, dimensional, ground speed, and ground heading data that are out of valid range end\n")

        # 7. 计算出轨迹的移动距离𝐷𝑖𝑠与速度*时间的最大距离
        df = df.groupby('MMSI').apply(calculate_distance).reset_index(drop=True)
        print("7 Calculate the maximum distance travelled by the trajectory 𝐷𝑖𝑠 with velocity*time end\n")

        # 8. 删除移动距离大于最大距离的异常值
        df = df[df['Distance'] <= df['MaxDistance']].reset_index(drop=True)
        print("8 Remove outliers with a travel distance greater than the maximum distance end\n")

        # 9. 增加一列 ISSIMILAR，标记是否为相似轨迹
        df['ISSIMILAR'] = 0
        print("9 Add a column ISSIMILAR to mark whether the trajectories are similar or not end\n")

        # 10. 基于改进的动态滑动窗口策略对AIS轨迹进行处理
        df = df.groupby('MMSI').apply(dynamic_window, np.array(
            [0.01, 0.05, 0.05, 0.1, 0.1, 0.05, 0.05, 0.1, 0.05, 0.05, 0.1, 0.05, 0.05, 0.05, 0.05, 0.1]), 500, 1000).reset_index(drop=True)
        print("10 Processing of AIS trajectories based on an improved dynamic sliding window strategy end\n")

        # 将清理后的数据保存到新文件中
        output_file_path = os.path.join(output_folder, filename)
        df.to_csv(output_file_path, index=False)
        print(f"Data cleansing is complete and saved to: {output_file_path}")
