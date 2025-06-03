import pandas as pd
import os
from pyproj import Transformer
from constants import *
from geopy.distance import geodesic, distance
import math


def wgs84_to_utm(northing, western):
    transformer = Transformer.from_crs("epsg:4326", "epsg:4575")
    lat, lon = transformer.transform(northing, western)
    return lat, lon


def trips_diff(df):
    # 将每个部分转换为列表

    print(f"trip length{len(df)}")

    grouped = df.groupby('MMSI')

    delete_index = []

    count = 0

    for mmsi, group in grouped:
        last_point = None

        for idx, row in group.iterrows():
            # print(idx)
            # if count % 100000 == 0:
            #     print(count)
            # count += 1

            if idx % 100000 == 0:
                print(idx)


            lat = row['LAT']
            lon = row['LON']
            point = (lat, lon)

            if last_point is None:
                last_point = point
                continue

            # 使用 geodesic 计算两点之间的距离
            # dis = geodesic(last_point, point).meters
            dis = math.sqrt((point[0] - last_point[0]) ** 2 + (point[1] - last_point[1]) ** 2)

            if dis <= distance_min:
                # 记录需要删除的索引
                delete_index.append(idx - 1)

            last_point = point

    df = df.drop(index = delete_index, inplace = True)



def trip(df):
    # 初始化一个变量用于存储递增的 count
    point_count = 0
    count = 0

    # 对每个 mmsi 分组
    for mmsi, group in df.groupby('MMSI'):
        # 初始化一个变量用于存储上一个 BaseDateTime
        last_base_date_time = None
        # print(df.head())
        for index, point in group.iterrows():
            # 获取当前组的第一个 BaseDateTime
            base_date_time = point['BaseDateTime']

            # 如果这是第一次遇到这个 mmsi，或者 BaseDateTime 大于 200，重置 incremental_count
            if last_base_date_time is None :
                last_base_date_time = base_date_time
                df.at[index, 'COUNT'] = count
                continue

            if (base_date_time - last_base_date_time) >= time_max or (base_date_time - last_base_date_time) <= time_min or point_count >= 60 :
                count += 1
                point_count = 0

            # 更新 'COUNT' 列
            df.at[index, 'COUNT'] = count

            point_count += 1

            last_base_date_time = base_date_time



def save_file(df, output_path, new_filename):
    # 保存处理后的数据集
    output_path = os.path.join(output_path, new_filename)
    df.to_csv(output_path, index=True)


def trip_count(data_format, data_name):
    data_path = os.path.join('/home/goha/DocumentsG/Goha/Goha/data', 'AIS', data_name)
    if data_format == 'csv':
        df = pd.read_csv(os.path.join(data_path, 'cleaned_'+ data_name +'.csv'))
        print('trip_count read finish')

        # 只保留部分
        df = df[['MMSI', 'BaseDateTime', 'LAT', 'LON']]

        # 将时间字符串转换为 datetime 对象
        # 将 datetime 对象转换为 Unix 时间戳（秒）
        df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
        df['BaseDateTime'] = df['BaseDateTime'].apply(lambda x: x.timestamp())

        # 将 经纬度 对象转换 （米）
        df['LAT'], df['LON'] = wgs84_to_utm (df['LAT'], df['LON'])
        print('data trans finish')

        trips_diff(df)
        save_file(df, data_path, 'diff_dis_'+ data_name +'.csv')
        print('delete distance finish')

        df['COUNT'] = -1
        trip(df)
        save_file(df, data_path, 'count_'+ data_name +'.csv')
        print('trip count finish')

        df = df.groupby('COUNT').filter(lambda x: x['COUNT'].count() >= trip_count_min)
        save_file(df, data_path, 'delete_count_'+ data_name +'.csv')
        print('delete finish')

        print('finish')

        # 显示 DataFrame 的前几行以确认数据是否正确加载
        # print(df.head())



# trip_count('csv', 'AIS_z')
