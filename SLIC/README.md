# SLIC
## Abstract

SLIC (Simple Linear Iterative Clustering) is an image segmentation algorithm that divides an image into superpixels. Superpixels are groups of pixels that are spatially contiguous and similar in color or intensity. 

## Run

Python Version: <img src=https://img.shields.io/badge/3.11.6-8A2BE2 />

```
pip install -r requirements.txt
python .\src\main.py
```

There are four parameters that can be changed in `main.py` :

* `image_path` : Path of the image to do SLIC.
* `k` : The number of clusters.
* `m` : The weight relationship between color and space.
* `iteration_time` : The number of algorithm iterations.

## Result

<center class="half">
<img src=".\assets\lenna.png" width=30%/>
<img src=".\results\lenna_K100_M0.2\Iteration10.png" width=30%/>
</center>




## Reference

[1]ACHANTA R, SHAJI A, SMITH K, et al. SLIC Superpixels Compared to State-of-the-Art Superpixel Methods[J/OL]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2012: 2274-2282. http://dx.doi.org/10.1109/tpami.2012.120. DOI:10.1109/tpami.2012.120.

