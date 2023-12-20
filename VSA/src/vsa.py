import random
from obj import OBJ
from triangle import Triangle
from queue import PriorityQueue
import tqdm
import os
from visualize import save_rendering


class Proxy:
    # each proxy is a plane in the 3D space
    def __init__(self, x, n):
        self.x = x
        self.n = n


class MyPriorityQueue:
    def __init__(self, distance, triangle, proxy):
        # each element in the priority queue is a tuple of (distance, triangle, proxy)
        self.distance = distance
        self.triangle = triangle
        self.proxy = proxy

    def __gt__(self, other):
        return self.distance > other.distance

    def __eq__(self, other):
        return self.distance == other.distance


class VSA:
    # Vertex Simplification Algorithm
    def __init__(self, model: OBJ, k: int):
        self.model = model
        self.triangles = self.model.triangles
        self.k = k
        # initialize regions(use index) and proxies
        self.regions = [[] for _ in range(self.k)]
        self.proxies = []
        # initialize labels and distances
        self.labels = [-1 for _ in range(len(self.triangles))]
        self.distances = [1e9 for _ in range(len(self.triangles))]
        self.conquered = [False for _ in range(len(self.triangles))]

    @staticmethod
    def get_distance(n1, n2):
        # get distance between two normal vectors
        return (n1[0] - n2[0]) ** 2 + (n1[1] - n2[1]) ** 2 + (n1[2] - n2[2]) ** 2

    def get_tp_distance(self, t: Triangle, p: Proxy):
        # get distance between a triangle and a proxy
        # use the distance of the normal vector difference and the area of the triangle
        return t.area() * self.get_distance(t.n, p.n)

    def get_rp_distance(self, region, proxy):
        # get distance between a region and a proxy
        # equal to the sum of the distances between the triangles and the proxy
        rp_distance = 0
        for tid in region:
            rp_distance += self.get_tp_distance(self.triangles[tid], proxy)
        return rp_distance

    def initialize_regions_and_proxies(self):
        # generate k different random integer between 0 and len(triangles)
        random_indices = random.sample(range(len(self.triangles)), self.k)
        # initialize regions and proxies
        for i in range(self.k):
            # add a triangle to each region
            triangle = self.triangles[random_indices[i]]
            self.regions[i].append(random_indices[i])
            # add a proxy
            self.proxies.append(Proxy(triangle.v1, triangle.n))
            # make sure each region only has one triangle
            assert len(self.regions[i]) == 1

    def create_priority_queue(self):
        # initialize priority queue at first time
        pq = PriorityQueue()

        for i in range(self.k):
            # put the triangle in the region into the priority queue
            tid = self.regions[i][0]
            triangle = self.triangles[tid]
            pq.put(MyPriorityQueue(self.get_tp_distance(triangle, self.proxies[i]),
                                   triangle,
                                   self.proxies[i]))
            # mark the triangle as conquered
            self.conquered[tid] = True

            # consider adjacent triangles
            adjacent_triangles = self.model.get_adjacent_triangles(triangle)
            for adjacent_triangle in adjacent_triangles:
                # put the adjacent triangles into the priority queue
                pq.put(MyPriorityQueue(self.get_tp_distance(adjacent_triangle, self.proxies[i]),
                                       adjacent_triangle,
                                       self.proxies[i]))
        return pq

    def recalculate_regions(self):
        # create priority queue at other times

        for i in range(self.k):
            pq = PriorityQueue()

            # get the region
            region = self.regions[i]
            # get the proxy
            proxy = self.proxies[i]

            for tid in region:
                # get the triangle
                triangle = self.triangles[tid]
                # put the triangle into the priority queue
                pq.put(MyPriorityQueue(self.get_tp_distance(triangle, proxy),
                                       triangle,
                                       proxy))

            self.regions[i] = [self.triangles.index(pq.get().triangle)]
            # make sure each region only has one triangle
            assert len(self.regions[i]) == 1

    def grow_regions(self, pq: PriorityQueue):
        while pq.qsize() > 0:
            # get the triangle with the smallest distance
            tp = pq.get()
            triangle = tp.triangle
            proxy = tp.proxy

            # check if the triangle is conquered
            tid = self.triangles.index(triangle)
            if self.conquered[tid]:
                continue

            # add the triangle to the region
            pid = self.proxies.index(proxy)
            region = self.regions[pid]
            region.append(tid)
            # mark the triangle as conquered
            self.conquered[tid] = True

            # consider adjacent triangles
            adjacent_triangles = self.model.get_adjacent_triangles(triangle)
            for adjacent_triangle in adjacent_triangles:
                # put the adjacent triangles into the priority queue
                pq.put(MyPriorityQueue(self.get_tp_distance(adjacent_triangle, proxy),
                                       adjacent_triangle,
                                       proxy))

    def geometry_partition(self, times):
        self.conquered = [False for _ in range(len(self.triangles))]
        if times == 0:
            # initialize regions and proxies
            self.initialize_regions_and_proxies()
        else:
            # recalculate regions
            self.recalculate_regions()

        # initialize priority queue
        pq = self.create_priority_queue()
        # grow regions
        self.grow_regions(pq)
        self.get_global_error()

    def get_global_error(self):
        # get the global error
        global_error = 0
        for i in range(self.k):
            # get the region
            region = self.regions[i]
            # get the proxy
            proxy = self.proxies[i]
            # get the region-proxy distance
            rp_distance = self.get_rp_distance(region, proxy)
            # add the distance to the global error
            global_error += rp_distance
        print("global error:{}".format(global_error))
        return global_error

    def proxy_adjustment(self):
        # adjust the proxies
        for i in range(self.k):
            # get the region
            region = self.regions[i]
            # get the proxy
            proxy = self.proxies[i]
            # compute the new proxy's normal vector
            new_n = [0, 0, 0]
            for tid in region:
                triangle = self.triangles[tid]
                triangle_size = triangle.area()
                new_n[0] += triangle.n[0] * triangle_size
                new_n[1] += triangle.n[1] * triangle_size
                new_n[2] += triangle.n[2] * triangle_size
            # normalize the new normal vector
            new_n_squared = (new_n[0] ** 2 + new_n[1] ** 2 + new_n[2] ** 2) ** 0.5
            new_n[0] /= new_n_squared
            new_n[1] /= new_n_squared
            new_n[2] /= new_n_squared

            # compute the new proxy's x coordinate by baricentric coordinates
            new_x = [0, 0, 0]
            for tid in region:
                triangle = self.triangles[tid]
                new_x[0] += triangle.v1[0]
                new_x[1] += triangle.v2[0]
                new_x[2] += triangle.v3[0]
            new_x[0] /= len(region)
            new_x[1] /= len(region)
            new_x[2] /= len(region)

            # update the proxy
            proxy.n = new_n
            proxy.x = new_x

    def train(self, iteration):
        for i in tqdm.tqdm(range(iteration)):
            directory = '../result/bunny_K{}'.format(self.k)
            if not os.path.exists(directory):
                os.makedirs(directory)
            self.geometry_partition(i)
            self.proxy_adjustment()
            filename = '{}/bunny_Iteration{}.png'.format(directory, i + 1)
            save_rendering(filename, self.triangles, self.regions)


