import numpy as np
import pandas as pd
import os


def trip_to_trips(df):
    # 使用groupby方法按照'count'列进行分组
    grouped = df.groupby('COUNT')

    # 创建新的DataFrame用于存储结果
    trips_df = pd.DataFrame(columns=['id', 'trips', 'trip_length'])

    # 遍历每个分组
    for count, group in grouped:
        # if count % 20000 == 0:
        #     print(count)
        group['GRID'] = np.int64(group['GRID'])
        group['BaseDateTime'] = np.int64(group['BaseDateTime'])
        # 提取需要的列
        selected_columns = group[['GRID', 'LON', 'LAT', 'BaseDateTime']].astype(str)

        # 将每条数据转换为字符串形式
        str_data = selected_columns.apply(lambda row: ','.join(row), axis=1)

        # 合并每组数据，并用分号分隔
        combined_str = ';'.join(str_data.values)

        # 计算当前组的长度
        trip_length = len(group)

        # 添加到结果DataFrame
        trips_df = pd.concat([trips_df, pd.DataFrame({'id': [count], 'trips': [combined_str], 'trip_length': [trip_length]}, index=[count])], ignore_index=True)

    # 重置索引以确保索引连续
    # trips_df = trips_df.sort_index().reset_index(names='COUNT')

    return trips_df


def save_file(df, output_path, new_filename):
    # 保存处理后的数据集
    output_path = os.path.join(output_path, new_filename)
    df.to_csv(output_path, index=False)

def trip2trips(data_format, data_name):
    data_path = os.path.join('/home/goha/DocumentsG/Goha/Goha/data', 'AIS', data_name)
    if data_format == 'csv':
        df = pd.read_csv(os.path.join(data_path, 'grid_cleaned_'+ data_name +'.csv'))
        print('trip2trips read finish')

        # 只保留部分
        df = df[['MMSI', 'BaseDateTime', 'LAT', 'LON', 'COUNT', 'GRID']]

        trips_df = trip_to_trips(df)
        # print(trips_df.head())

        save_file(trips_df, data_path, 'trips_cleaned_'+ data_name +'.csv')

        print('trips finish')

        print('finish')

# trip2trips('csv', 'AIS_z')