# ICP

## Abstract

ICP(Iterative Closest Point) is a Point Cloud Registration method refers to the input of two point clouds and let them overlap as much as possible. The transformation here only consider rigidbody.

## Run

Python Version: <img src=https://img.shields.io/badge/3.9.18-8A2BE2 />

```
pip install -r requirements.txt
python .\src\main.py
```

There are one parameters that can be changed in `main.py` :

* `max_iteration` : The number of algorithm iterations.

## Result

<center class="half">
<img src=".\results\1\1_initial.png" width=150/>
<img src=".\results\1\1_iter_9.png" width=150/>
</center>


## Reference

[1]BESL P J, MCKAY N D. &lt;title&gt;Method for registration of 3-D shapes&lt;/title&gt;[C/OL]//SPIE Proceedings,Sensor Fusion IV: Control Paradigms and Data Structures. 1992. http://dx.doi.org/10.1117/12.57955. DOI:10.1117/12.57955.
