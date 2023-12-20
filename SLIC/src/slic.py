import os
import tqdm
import numpy as np
from skimage import io, color


class Image:
    @staticmethod
    def open(path):
        # open image and convert to LAB
        image_rgb = io.imread(path)
        image_lab = color.rgb2lab(image_rgb)
        return image_lab

    def __init__(self, path):
        # open image
        self.data = self.open(path)
        # record name
        self.name = os.path.splitext(os.path.basename(path))[0]
        # record height and width
        self.height = self.data.shape[0]
        self.width = self.data.shape[1]

    def get_lab(self, x, y):
        # get lab value at x,y
        return self.data[x, y, :]

    def get_gradient(self, x, y):
        # get gradient at x_l,x_r,y_u,y_d
        gradient_x_l = self.get_lab(x - 1, y) if x - 1 >= 0 else 0
        gradient_x_r = self.get_lab(x + 1, y) if x + 1 < self.width else 0
        gradient_y_u = self.get_lab(x, y - 1) if y - 1 >= 0 else 0
        gradient_y_d = self.get_lab(x, y + 1) if y + 1 < self.height else 0
        # calculate gradient on x,y axis
        gradient_x = (gradient_x_l[0] - gradient_x_r[0]) ** 2 +\
                     (gradient_x_l[1] - gradient_x_r[1]) ** 2 +\
                     (gradient_x_l[2] - gradient_x_r[2]) ** 2
        gradient_y = (gradient_y_u[0] - gradient_y_d[0]) ** 2 +\
                     (gradient_y_u[1] - gradient_y_d[1]) ** 2 +\
                     (gradient_y_u[2] - gradient_y_d[2]) ** 2
        return (gradient_x + gradient_y) ** 0.5

    def get_distance(self, x, y, pixel):
        # get distance between pixel[x][y] and another pixel
        cie_l, cie_a, cie_b = self.get_lab(x, y)
        distance_lab = ((cie_l - pixel.cie_l) ** 2 + (cie_a - pixel.cie_a) ** 2 + (cie_b - pixel.cie_b) ** 2) ** 0.5
        distance_xy = ((x - pixel.x) ** 2 + (y - pixel.y) ** 2) ** 0.5
        return distance_lab, distance_xy

    def save(self, path):
        # save lab image as rgb
        image_rgb = color.lab2rgb(self.data)
        # rescales 0-1 to 0-255
        image_rgb_255 = (image_rgb * 255).astype(np.uint8)
        io.imsave(path, image_rgb_255)


class Cluster:
    def __init__(self, cid, x, y, cie_l=0, cie_a=0, cie_b=0):
        # a cluster has a center pixel and a list of pixels
        self.set(cid, x, y, cie_l, cie_a, cie_b)
        self.pixels = []

    def set(self, cid, x, y, cie_l, cie_a, cie_b):
        # set id and x,y and l,a,b
        self.cid = cid
        self.x = x
        self.y = y
        self.cie_l = cie_l
        self.cie_a = cie_a
        self.cie_b = cie_b


class SLIC:
    def __init__(self, image: Image, k: int, m: float):
        # set image and k,m and n,s
        self.image = image
        self.k = k
        self.m = m
        self.n = self.image.height * self.image.width
        self.s = int((self.n / self.k) ** 0.5)
        # set clusters and labels and distances
        self.clusters = []
        self.labels = [[-1 for _ in range(self.image.height)] for _ in range(self.image.width)]
        self.distances = [[1e9 for _ in range(self.image.height)] for _ in range(self.image.width)]

    def initialize_clusters(self):
        # iterate through image by step size
        for x in range(self.s // 2, self.image.width, self.s):
            for y in range(self.s // 2, self.image.height, self.s):
                # create cluster
                cie_l, cie_a, cie_b = self.image.get_lab(x, y)
                cluster = Cluster(len(self.clusters), x, y, cie_l, cie_a, cie_b)
                self.clusters.append(cluster)

    def adjust_clusters(self):
        for cluster in self.clusters:
            # calculate 9 pixels' gradients around each center
            old_gradient = self.image.get_gradient(cluster.x, cluster.y)
            for x in range(cluster.x - 1, cluster.x + 2):
                for y in range(cluster.y - 1, cluster.y + 2):
                    new_gradient = self.image.get_gradient(x, y)
                    # update cluster if gradient is smaller
                    if new_gradient < old_gradient:
                        cie_l, cie_a, cie_b = self.image.get_lab(x, y)
                        cluster.set(cluster.cid, x, y, cie_l, cie_a, cie_b)

    def update_labels(self):
        for cluster in self.clusters:
            # iterate through 2S*2S pixels in cluster
            for x in range(cluster.x - 2 * self.s, cluster.x + 2 * self.s):
                for y in range(cluster.y - 2 * self.s, cluster.y + 2 * self.s):
                    # skip if out of bound
                    if x < 0 or x >= self.image.width or y < 0 or y >= self.image.height:
                        continue
                    # update label if distance is smaller
                    dist_lab, dist_xy = self.image.get_distance(x, y, cluster)
                    dist = (dist_lab ** 2 + self.m * dist_xy ** 2) ** 0.5
                    if dist < self.distances[x][y]:
                        # update cluster's pixels
                        if self.labels[x][y] != -1:
                            self.clusters[self.labels[x][y]].pixels.remove((x, y))
                        # update distance and label
                        self.labels[x][y] = cluster.cid
                        self.distances[x][y] = dist
                        cluster.pixels.append((x, y))

    def update_clusters(self):
        for cluster in self.clusters:
            # update new center
            sum_x = sum_y = count = 0
            for pixel in cluster.pixels:
                sum_x += pixel[0]
                sum_y += pixel[1]
                count += 1
            # x,y is calculated by average of pixels
            new_x = sum_x // count
            new_y = sum_y // count
            cie_l, cie_a, cie_b = self.image.get_lab(new_x, new_y)
            cluster.set(cluster.cid, new_x, new_y, cie_l, cie_a, cie_b)

    def update_image(self, path: str):
        image_lab = self.image.data
        for cluster in self.clusters:
            # set pixels to cluster's color
            for pixel in cluster.pixels:
                image_lab[pixel[0], pixel[1], :] = cluster.cie_l, cluster.cie_a, cluster.cie_b
        # save image
        self.image.data = image_lab
        self.image.save(path)

    def train(self, iterations: int):
        # create directory
        train_name = '{n}_K{k}_M{m}'.format(n=self.image.name, k=self.k, m=self.m)
        print('Training {} Start!'.format(train_name))
        directory = f'../results/{train_name}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        # initialize clusters and adjust by gradients
        self.initialize_clusters()
        self.adjust_clusters()
        for _ in tqdm.tqdm(range(iterations)):
            # update labels and clusters
            self.update_labels()
            self.update_clusters()
            # update image every iteration
            self.update_image('{}/Iteration{}.png'.format(directory, _ + 1))
