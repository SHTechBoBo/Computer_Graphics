from icp import *

max_iteration = 10

if __name__ == '__main__':
    for i in range(1, 10):
        pc1 = PointCloud(path="../assets/{}_A.txt".format(i))
        pc2 = PointCloud(path="../assets/{}_B.txt".format(i))
        icp = ICP(pc1, pc2, name="{}".format(i))
        icp.train(max_iter=max_iteration)
