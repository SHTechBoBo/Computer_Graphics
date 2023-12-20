class Triangle:
    def __init__(self, v1, v2, v3, n):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.n = n

    def area(self):
        # calculate the area of a triangle
        l1 = self.v2 - self.v1
        l2 = self.v3 - self.v1
        # calculate cross product
        cp = (l1[0] * l2[1] - l1[1] * l2[0],
              l1[1] * l2[2] - l1[2] * l2[1],
              l1[2] * l2[0] - l1[0] * l2[2])
        # return the length of the cross product divided by 2
        return (cp[0] ** 2 + cp[1] ** 2 + cp[2] ** 2) ** 0.5 / 2

    # iterable
    def __iter__(self):
        yield self.v1
        yield self.v2
        yield self.v3

    # subscriptable
    def __getitem__(self, item):
        if item == 0:
            return self.v1
        elif item == 1:
            return self.v2
        elif item == 2:
            return self.v3
        else:
            assert False, 'index out of range'

