# GOES Solar Retriever

The solar data from the GOES satellite is stored in an [FTP server](https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/).
This tool allows for easy retrieval of the data in Python. 

## Install
```pip install goes-solar-retriever ```

## Example
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

## TODO:
* Provide full support for products other than SUVI. 
