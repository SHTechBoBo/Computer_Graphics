import numpy as np
import tqdm
import os
from scipy.spatial import KDTree
from mayavi import mlab


class PointCloud:
    @staticmethod
    def get_points_from_txt(path):
        points = np.loadtxt(path, delimiter=' ', dtype=np.float32)
        return points

    def __init__(self, path):
        if path:
            self.points = self.get_points_from_txt(path)

    def get_centroid(self):
        # calculate centroid
        # (x1 + x2 + x3 + ... + xn) / n
        return np.mean(self.points, axis=0)


class ICP:
    def __init__(self, pc_source, pc_target, name):
        # point cloud source & target
        self.pc_source = pc_source
        self.pc_target = pc_target
        self.pc_temp = None
        self.name = name

        # translation & rotation matrix
        # T = [tx, ty, tz]
        # R = [[r11, r12, r13],
        #      [r21, r22, r23],
        #      [r31, r32, r33]]
        self.T = np.zeros(3)
        self.R = np.identity(3)

        # closest point pair & threshold
        self.closest_pair = [-1 for _ in range(len(self.pc_source.points))]
        self.threshold = 1e-5

    def transformation_source_point_cloud(self):
        # transform source point cloud
        # according to matrix T & R
        transformation_matrix = np.eye(4)
        transformation_matrix[0:3, 0:3] = self.R
        transformation_matrix[0:3, 3] = self.T.reshape(1, 3)

        # homogeneous coordinates
        pc_homogeneous = np.hstack((self.pc_temp.points, np.ones((self.pc_temp.points.shape[0], 1))))
        self.pc_temp.points = (np.dot(transformation_matrix, pc_homogeneous.T)).T[:, :3]

    def get_closest_pair(self):
        # for every point in temp point cloud,
        # find the closest point in target point cloud
        for i in range(len(self.pc_temp.points)):
            p_s = self.pc_temp.points[i]
            min_dist = float('inf')
            for j in range(len(self.pc_target.points)):
                p_t = self.pc_target.points[j]
                dist = np.linalg.norm(p_s - p_t)
                if dist < min_dist:
                    min_dist = dist
                    self.closest_pair[i] = j
                    # break if distance is smaller than threshold
                    if dist < self.threshold:
                        break

    def get_closest_pair_kdtree(self):
        # for every point in temp point cloud,
        # find the closest point in target point cloud
        # build KDTree
        kdtree = KDTree(self.pc_target.points)
        sum_dist = 0
        for i in range(len(self.pc_temp.points)):
            p_s = self.pc_temp.points[i]
            dist, idx = kdtree.query(p_s)
            sum_dist += dist
            self.closest_pair[i] = idx
        # check if average distance is smaller than threshold
        print("average distance: {}".format(sum_dist / len(self.pc_temp.points)))
        if sum_dist / len(self.pc_temp.points) < self.threshold:
            return True
        else:
            return False

    def calculate_svd(self):
        # H = sigma(p_s * p_t.T)
        # H = np.zeros((3, 3))
        centroid_s = self.pc_temp.get_centroid()
        centroid_t = self.pc_target.get_centroid()

        p_s = self.pc_temp.points - centroid_s
        # use closest pair to construct p_t
        p_t = np.array([self.pc_target.points[i] for i in self.closest_pair]) - centroid_t

        H = p_s.T.dot(p_t)
        U, S, V = np.linalg.svd(H)
        self.R = (V.T).dot(U.T)
        self.T = centroid_t - self.R.dot(centroid_s)

    def train(self, max_iter=10):
        # initialize temp point cloud
        self.pc_temp = PointCloud(path=None)
        self.pc_temp.points = self.pc_source.points.copy()

        # make a directory to store results
        path = "../results/{}/".format(self.name)
        if not os.path.exists(path):
            os.makedirs(path)
        self.save_figure(path + self.name + "_initial.png")

        # iteration
        for i in tqdm.tqdm(range(max_iter)):
            self.transformation_source_point_cloud()
            # self.get_closest_pair()
            if self.get_closest_pair_kdtree():
                break
            self.calculate_svd()
            self.save_figure(path + self.name + "_iter_{}.png".format(i))

    def save_figure(self, name):
        # close screen and set size
        mlab.options.offscreen = True
        figure = mlab.figure(bgcolor=(1, 1, 1), size=(1920, 1080))

        self.transformation_source_point_cloud()
        point_cloud_np1 = self.pc_temp.points
        point_cloud_np2 = self.pc_target.points

        # visualize point cloud after transformation
        mlab.points3d(point_cloud_np1[:, 0], point_cloud_np1[:, 1], point_cloud_np1[:, 2],
                      mode='point',
                      color=(0, 1, 0),  # green
                      scale_factor=1,
                      figure=figure)

        # visualize target point cloud
        mlab.points3d(point_cloud_np2[:, 0], point_cloud_np2[:, 1], point_cloud_np2[:, 2],
                      mode='point',
                      color=(1, 0, 0),  # red
                      scale_factor=1,
                      figure=figure)

        # save figure
        mlab.savefig(name, figure=figure)
        mlab.close(figure)


