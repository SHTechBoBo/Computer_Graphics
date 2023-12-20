from obj import OBJ
from vsa import VSA

obj_path = OBJ('../asset/bunny.obj')
K = 100
iteration_time = 10

if __name__ == '__main__':
    vsa1 = VSA(obj_path, K)
    vsa1.train(iteration_time)

