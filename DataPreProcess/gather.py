import os
import pandas as pd


def save_file(df, output_path, new_filename):
    # 保存处理后的数据集
    output_path = os.path.join(output_path, new_filename)
    df.to_csv(output_path, index=False)


def gather():
    input_folder = '/home/goha/DocumentsG/Goha/Goha/data/AIS/AIS/AIS_new'
    df = pd.DataFrame()
    lon_min = [-95.5, -94.8,  -91.18, -88.7, -85.6]
    lon_max = [-83.5, -91.18, -89.5,  -85.6, -83.5]
    lat_min = [ 23.5,  28.8,   28.8,   28.8,  28.8]
    lat_max = [ 28.8,  29.2,   29.0,   30.0,  29.5]
    # lon_min = [-95.5]
    # lon_max = [-83.5]
    # lat_min = [23.5]
    # lat_max = [28.8]
    # 遍历所有的csv文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_folder, filename)

            print(f"{filename} begin")
            # 读取csv文件的内容
            temp_df = pd.read_csv(file_path)

            # 只保留部分
            temp_df = temp_df[['MMSI', 'BaseDateTime', 'LAT', 'LON']]

            # temp_df = temp_df[((temp_df['LON'] >= lon_min[0]) & (temp_df['LON'] <= lon_max[0]) & (temp_df['LAT'] >= lat_min[0]) & (temp_df['LAT'] <= lat_max[0]))
            #                   | ((temp_df['LON'] >= lon_min[1]) & (temp_df['LON'] <= lon_max[1]) & (temp_df['LAT'] >= lat_min[1]) & (temp_df['LAT'] <= lat_max[1]))
            #         ]

            # 使用zip来组合纬度和经度范围
            conditions = zip(lon_min, lon_max, lat_min, lat_max)

            for lon_min, lon_max, lat_min, lat_max in conditions:
                df = pd.concat([df, temp_df[((temp_df['LON'] >= lon_min) & (temp_df['LON'] < lon_max) &
                                   (temp_df['LAT'] >= lat_min) & (temp_df['LAT'] < lat_max))]])
                # temp_df = temp_df[((temp_df['LON'] >= lon_min) & (temp_df['LON'] < lon_max) &
                #                    (temp_df['LAT'] >= lat_min) & (temp_df['LAT'] < lat_max))]


            # 将读取的内容添加到df中
            # df = pd.concat([df, temp_df])
            print(f"{filename} end")

            # break

    save_file(df, 'D:/gohak/data/AIS/AIS_WEST', 'AIS_WEST.csv')
    print("finish")


gather()


