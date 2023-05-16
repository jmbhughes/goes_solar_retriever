# GOES Solar Retriever

The solar data from the GOES satellite is stored on an [FTP server](https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/).
This tool allows for easy retrieval of the data in Python. 

## Install
```pip install goes-solar-retriever ```

## Examples
```python 
from datetime import datetime
from goessolarretriever import Retriever, Satellite, Product
satellite = Satellite.GOES16
product = Product.suvi_l2_ci195

# Retrieve every hundredth image between two time periods
start = datetime(2020, 3, 15)
end = datetime(2020, 3, 20)
r = Retriever()
results = r.search(satellite, product, start, end)
r.retrieve(results[::100], "/home/marcus/Desktop/imgs/")

# Retrieve the image closest to a time
time = datetime(2020, 3, 15, 12, 0)
r = Retriever()
filename = r.retrieve_nearest(satellite, product, time, "/home/marcus/Desktop/imgs/")
``` 

## Satellites included:
* GOES 16: `Satellite.GOES16`
* GOES 17: `Satellite.GOES17`

## Products included:
* 94 angstrom composite: `Product.suvi_l2_ci094`
* 131 angstrom composite: `Product.suvi_l2_ci131`
* 171 angstrom composite: `Product.suvi_l2_ci171`
* 195 angstrom composite: `Product.suvi_l2_ci195`
* 284 angstrom composite: `Product.suvi_l2_ci284`
* 304 angstrom composite: `Product.suvi_l2_ci304`
* 94 ansgstrom L1b: `Product.suvi_l1b_fe094`
* 131 angstrom L1b: `Product.suvi_l1b_fe131`
* 171 angstrom L1b: `Product.suvi_l1b_fe171`
* 195 angstrom L1b: `Product.suvi_l1b_fe195`
* 284 angstrom L1b: `Product.suvi_l1b_fe284`
* 304 angstrom L1b: `Product.suvi_l1b_he304`
* SUVI thematic maps: `Product.suvi_l2_thmap`

## TODO:
* Provide full support for products other than SUVI. 
* Add documentation
* Create tests
* Make a progress bar show up when searching
