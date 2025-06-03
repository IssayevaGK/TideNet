import itertools
import numpy as np


def euclidean_distance(p1, p2):
    # """计算两点之间的欧氏距离"""
    # print(p1, p2)
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

def is_increasing(arr):
    """ 检查数组是否递增 """
    return all(arr[i] < arr[i + 1] for i in range(len(arr) - 1))

def find_closest_points(traj, extra_points):
    # 在traj中找到与extra_points最近的三个点，保持顺序不变
    min_distance = float('inf')
    closest_points = None


    # 遍历所有可能的三个点的组合
    for indices in itertools.combinations(range(len(traj)), len(extra_points)):
        # print(indices)
        # 确保找到的三个点的索引按顺序排列
        if is_increasing(indices):
            subseq = [traj[i] for i in indices]

            # 计算每个对应点对之间的距离之和
            total_distance = sum(euclidean_distance(subseq[j], extra_points[j]) for j in range(len(extra_points)))

            # 如果找到了更小的总距离，则更新结果
            if total_distance < min_distance:
                min_distance = total_distance
                closest_points = subseq

    return closest_points, min_distance


# 示例数据
traj = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11)]
extra_points = [(2, 3), (4, 5), (6, 7),(10,8)]

# 找到最接近extra_points的三个点
closest_points, distance = find_closest_points(traj, extra_points)

print("Closest Points:", closest_points)
print("Minimum Distance:", distance)