# VSA
## Abstract

VSA(Variational Shape Approximation) streamlines complex 3D shapes into simpler representations, optimizing for fewer elements while preserving visual fidelity using an iterative approach.

## Run

Python Version: <img src=https://img.shields.io/badge/3.11.6-8A2BE2 />

```
pip install -r requirements.txt
python .\src\main.py
```

There are four parameters that can be changed in `main.py` :

* `obj_path` : Path of the obj to do VSA.
* `k` : The number of clusters.
* `iteration_time` : The number of algorithm iterations.

## Result

<center class="half">
<img src=".\results\bunny_K100\bunny_Iteration1.png" width=30%/>
<img src=".\results\bunny_K100\bunny_Iteration10.png" width=30%/>
</center>





## Reference

[1]COHEN-STEINER D, ALLIEZ P, DESBRUN M. Variational shape approximation[J/OL]. ACM Transactions on Graphics, 2004: 905-914. http://dx.doi.org/10.1145/1015706.1015817. DOI:10.1145/1015706.1015817.
