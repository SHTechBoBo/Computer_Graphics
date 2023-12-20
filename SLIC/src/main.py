from slic import *

image_path = Image("../assets/lenna.png")
k = 100
m = 0.2
iteration_time = 10


if __name__ == '__main__':
    SLIC(image_path, k, m).train(iteration_time)


