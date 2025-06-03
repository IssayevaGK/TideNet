import numpy as np
import pandas as pd
import os
from pyproj import Transformer
import pickle
from constants import *


def wgs84_to_utm(northing, western):
    transformer = Transformer.from_crs("epsg:4326", "epsg:4575")
    lat, lon = transformer.transform(northing,western)
    return lat, lon

# 用"epsg:4575"的网格转换
def create_grids(df):
    lat_min = df['LAT'].min()
    lon_min = df['LON'].min()
    lat_max = df['LAT'].max()
    lon_max = df['LON'].max()

    # print(lat_min, lon_min, lat_max, lon_max)

    # 每个网格的地面尺寸（米）
    # grid_side = 300

    # 生成网格
    grids = {}
    grids_id = 0
    for lat in np.arange(lat_min, lat_max, grid_side):
        for lon in np.arange(lon_min, lon_max, grid_side):
            grids[grids_id] = {
                'lat_min': lat,
                'lat_max': lat + grid_side,
                'lon_min': lon,
                'lon_max': lon + grid_side,
                'center_lat': lat + grid_side / 2,
                'center_lon': lon + grid_side / 2,
                'weight': 0
            }
            grids_id += 1
            # grids.append({
            #     'id': grids_id,
            #     'lat_min': lat,
            #     'lat_max': lat + grid_side,
            #     'lon_min': lon,
            #     'lon_max': lon + grid_side,
            #     'center_lat': lat + grid_side / 2,
            #     'center_lon': lon + grid_side / 2,
            #     'weight': 0
            # })

    return grids


# 给轨迹点加上网格号
def trip_grids(df, grids):

    print("df length:{}".format(len(df)))
    print("grids length:{}".format(len(grids)))

    # 每个网格的地面尺寸（米）
    # grid_side = 300

    lat_min = df['LAT'].min()
    lon_min = df['LON'].min()
    lat_max = df['LAT'].max()
    lon_max = df['LON'].max()

    lat_count = int((lat_max - lat_min) // grid_side)
    lon_count = int((lon_max - lon_min) // grid_side)

    if lat_max % grid_side != 0:
        lat_count += 1
    if lon_max % grid_side != 0:
        lon_count += 1

    for index, point in df.iterrows():
        if index % 50000 == 0:
            print(index)
        # 纬度方向上的网格索引
        if point['LAT'] == lat_min:
            lat_index = 0
        elif (point['LAT'] - lat_min) % grid_side == 0:
            lat_index = int((point['LAT'] - lat_min) // grid_side) - 1
        else:
            lat_index = int((point['LAT'] - lat_min) // grid_side)
        # 经度方向上的网格索引
        if point['LON'] == lon_min:
            lon_index = 0
        elif (point['LON'] - lon_min) % grid_side == 0:
            lon_index = int((point['LON'] - lon_min) // grid_side) - 1
        else:
            lon_index = int((point['LON'] - lon_min) // grid_side)

        grid_id = lon_index + lon_count * lat_index

        # print("lat_index :{}".format(lat_index))
        # print("lon_index :{}".format(lon_index))
        # print("grid_id :{}".format(grid_id))

        # 更新 'GRID' 列
        df.at[index, 'GRID'] = grid_id
        grids[grid_id]['weight'] += 1

        # if index == 0:
        #     print(f"lat_min {lat_min} lon_min {lon_min}")
        #     print(f"point {point}")
        #     print(f"lon_index {lon_index} lon_count {lon_count} lat_index {lat_index} lat_count {lat_count}")
        #     print(f"grids[grid_id] {grids[grid_id]}")
        #     print(grid_id)
        # grids.loc[grid_id, 'weight'] += 1



# 创建字典
def create_dict(grids):
    grids_dict = {}

    for i in range(len(grids)):
        if grids[i]['weight'] < grid_weight_min:
            continue

        grid_id = i
        center_lon = grids[i]['center_lon']
        center_lat = grids[i]['center_lat']
        grids_dict[grid_id] = (center_lon, center_lat)


    # for grid in grids:
    #     if grid['weight'] == 0:
    #         continue
    #
    #     grid_id = grid['id']
    #     center_lon = grid['center_lon']
    #     center_lat = grid['center_lat']
    #     grids_dict[grid_id] = (center_lon, center_lat)

    return grids_dict


def save_file(df, output_path, new_filename):
    # 保存处理后的数据集
    output_path = os.path.join(output_path, new_filename)
    df.to_csv(output_path, index=True)


def meshing(data_format, data_name):
    data_path = os.path.join('/home/goha/DocumentsG/Goha/Goha/data/AIS', 'AIS', data_name)
    if data_format == 'csv':
        df = pd.read_csv(os.path.join(data_path, 'delete_count_'+ data_name +'.csv'))
        print('meshing read finish')

        # 只保留部分
        df = df[['MMSI', 'BaseDateTime', 'LAT', 'LON', 'COUNT']]

        # 将时间字符串转换为 datetime 对象
        # 将 datetime 对象转换为 Unix 时间戳（秒）
        # df['BaseDateTime'] = pd.to_datetime(df['BaseDateTime'])
        # df['BaseDateTime'] = df['BaseDateTime'].apply(lambda x: x.timestamp())

        # 将 经纬度 对象转换 （米）
        # df['LAT'], df['LON'] = wgs84_to_utm (df['LAT'], df['LON'])
        # print('data trans finish')

        # 创建网格
        grids = create_grids(df)
        print('create grid finish')

        # 给轨迹点加上网格号
        trip_grids(df, grids)
        save_file(df, data_path, 'grid_cleaned_'+ data_name +'.csv')
        print('trip add grid finish')

        # 创建字典
        grids_dict = create_dict(grids)
        # 保存到pickle文件
        pickle.dump(grids_dict, open(os.path.join(data_path, 'grids_'+ data_name +'.pickle'), 'wb'))
        # 读取
        grids_AIS_WEST = pickle.load(open(os.path.join(data_path, 'grids_'+ data_name +'.pickle'), 'rb'))
        open(os.path.join(data_path, 'grids_'+ data_name +'.txt'), 'w').write(f"{grids_AIS_WEST}\n")
        print('create dict finish')

        print('finish')

        # 显示 DataFrame 的前几行以确认数据是否正确加载
        # print(df.head())


# meshing('csv', 'AIS_z')


