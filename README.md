# geo1015-ass4-team-bbq

# Getting started

## Install packages

```
pip install -r requirements.txt
```

or if you use Poetry

```
poetry install
```

## Configuration

To run this program, you need to check `config.py` which allows you to change several paramers for the program such as input file name and output file name.
To run this program with your arbitary input LAS file, you need to locate the data under the `data/input` directory and modify config.

## Run commands

### Run Step3, 4 and 5 together

```
make main
```

### Step3

```
make step3
```

### Step4

```
make step4
```

### Step5

```
make step5
```

# Overview of program

## Programs

`preprocess.py`:This file contains a couple functions for pre-processing such as thinning, remove outliers and clip data with bounding box.

`gftin.py`: The program which process ground filtering test. The class has functions to to return points passed ground test. In debug mode, it'll write GeoJSON file exporting TIN.

`tin.py`: This program create TIN with all of ground points. This class is the interface to create TIN and rasterise with arbitary extent.

`benchmark.py`: Benchmark can be obtains with this file. This file allows you to change three key parameters of ground filtering test and serves statistical result.

`ptio.py`: A file looks after IO.

`geojson.py`: A file to export points as GeoJSON file with specified coordinate transformation. This is mainly debug purpose.

`pipeline.py`: PDAL pipeline to run DBSCAN. The class and its functions allows you to change some parameters such as `eps` and `min_points` for DBSCAN.

`vegetation.py`: The class which extracts points of trees from unclassified points. Detail of implementaion is written in the report.

`step3.py`: main file of step3.
`step4.py`: main file of step4.
`step5.py`: main file of step5.
