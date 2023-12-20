import trimesh
from triangle import Triangle


class OBJ:
    @staticmethod
    def load(path):
        return trimesh.load(path)

    def __init__(self, filename):
        # load mesh
        self.mesh = self.load(filename)
        # record each triangle in the format of (v1, v2, v3, n)
        self.triangles = []
        for i in range(len(self.mesh.faces)):
            # get the vertices of the triangle
            v1 = self.mesh.vertices[self.mesh.faces[i][0]]
            v2 = self.mesh.vertices[self.mesh.faces[i][1]]
            v3 = self.mesh.vertices[self.mesh.faces[i][2]]
            # get the normal vector of the triangle
            n = self.mesh.face_normals[i]
            # create a triangle
            t = Triangle(v1, v2, v3, n)
            # add the triangle to the list
            self.triangles.append(t)

    def get_adjacent_triangles(self, triangle):
        # check if the triangle is in the mesh
        if triangle not in self.triangles:
            assert False, 'triangle not in the mesh'

        # get the adjacent triangles of a triangle
        adjacent_triangles = []
        for i in range(len(self.triangles)):
            # check if the triangle shares two vertices with the triangle
            count = 0
            for v in triangle:
                if (v[0] == self.triangles[i].v1[0] and
                        v[1] == self.triangles[i].v1[1] and
                        v[2] == self.triangles[i].v1[2]) or \
                   (v[0] == self.triangles[i].v2[0] and
                        v[1] == self.triangles[i].v2[1] and
                        v[2] == self.triangles[i].v2[2]) or \
                   (v[0] == self.triangles[i].v3[0] and
                        v[1] == self.triangles[i].v3[1] and
                        v[2] == self.triangles[i].v3[2]):
                    count += 1
            # skip count = 0 or 1 or 3
            if count == 2:
                adjacent_triangles.append(self.triangles[i])
        return adjacent_triangles


if __name__ == '__main__':
    obj = OBJ('bunny.obj')


