import pandas as pd
import numpy as np
import os
import math
import pickle
from geopy.distance import geodesic
# import haversine


def trips_diff(trips):
    # 将每个部分转换为列表

    print(f"trip length{len(trips)}")
    i = 0

    diff_time = {}
    diff_loc = {}

    for trip in trips:
        if i % 5000 == 0:
            print(i)
        i += 1

        last_base_date_time = None
        # last_base_loc = None

        # 按照逗号分割每一部分，并转换为相应的数据类型
        trip_point = trip.split(';')

        for loc in trip_point:
            idx, lon, lat, time = loc.split(',')

            # print(idx, lon, lat, time)

            base_date_time = int(time)
            base_loc = float(lat), float(lon)

            # 如果这是第一次遇到这个 mmsi，或者 BaseDateTime 大于 200，重置 incremental_count
            if last_base_date_time is None:
                last_base_date_time = base_date_time
                last_base_loc = base_loc
                continue

            time = base_date_time - last_base_date_time

            loc =  (math.sqrt((base_loc[0] - last_base_loc[0])**2 + (base_loc[1] - last_base_loc[1])**2))

            # loc = int(geodesic(last_base_loc, base_loc).meters)

            # loc = int(haversine(last_base_loc, base_loc))

            diff_time[time] = diff_time.get(time, 0) + 1
            diff_loc[loc] = diff_loc.get(loc, 0) + 1


            last_base_date_time = base_date_time
            last_base_loc = base_loc


    # 按照字典的值（计数）从大到小排序
    diff_time = sorted(diff_time.items(), key=lambda item: item[1], reverse=True)
    diff_loc = sorted(diff_loc.items(), key=lambda item: item[1], reverse=True)
    return diff_time, diff_loc


def save_file(df, output_path, new_filename):
    # 保存处理后的数据集
    output_path = os.path.join(output_path, new_filename)
    df.to_csv(output_path, index=True)


def gather_time_loc_diff(data_format, data_name):
    data_path = os.path.join('/home/goha/DocumentsG/Goha/Goha/data', 'AIS', data_name)
    if data_format == 'csv':
        df = pd.read_csv(os.path.join(data_path, 'traj_train.csv'))
        print('gather_time_loc_diff read finish')

        # print(df.head())

        # 计算diff_time
        diff_time, diff_loc = trips_diff(df['trips_new'])

        # print(diff_time)

        # 保存到pickle文件
        pickle.dump(diff_time, open(os.path.join(data_path, 'diff_time_AIS.pickle'), 'wb'))
        # 读取
        diff_time_AIS = pickle.load(open(os.path.join(data_path, 'diff_time_AIS.pickle'), 'rb'))
        open(os.path.join(data_path, 'diff_time_AIS.txt'), 'w').write(f"{diff_time_AIS}\n")

        # 保存到pickle文件
        pickle.dump(diff_loc, open(os.path.join(data_path, 'diff_loc_AIS.pickle'), 'wb'))
        # 读取
        diff_loc_AIS = pickle.load(open(os.path.join(data_path, 'diff_loc_AIS.pickle'), 'rb'))
        open(os.path.join(data_path, 'diff_loc_AIS.txt'), 'w').write(f"{diff_loc_AIS}\n")

        print('create dict finish')


        print('diff trip finish')


# gather_time_loc_diff('csv', 'AIS_z')