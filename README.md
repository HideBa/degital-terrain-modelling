## Getting Started

### Installing Packages

Install the required packages using pip:

```
pip install -r requirements.txt
```

If you install all dependencies with development packages

```
pip install -r requirements.dev.txt
```

Alternatively, if you use Poetry:

```
poetry install
```

### Configuration

To run this program, you should check `config.py`. This file allows you to modify several parameters, such as the input file name and output file name. To use your own LAS file, place it in the `data/input` directory and update the configuration accordingly.

> [!NOTE]
> The program performs pre-processing tasks, including thinning the LAS file and removing outliers. The first execution might take more time. Pre-processed files are saved under the `data/input` directory, which speeds up subsequent runs.

## Run Commands

> [!NOTE]
> Due to the high time complexity of the ground filtering algorithm and interpolation, processing a 500m by 500m extent can take a considerable amount of time. For testing purposes, it is recommended to use a smaller extent, such as 100m by 100m. This can be adjusted in `config.py`.

### Running Steps 3, 4, and 5 Together

```
make main
```

### Step 3

```
make step3
```

### Step 4

```
make step4
```

### Step 5

```
make step5
```

## Overview of the Program

### Modules

- `preprocess.py`: Contains functions for pre-processing, such as thinning, outlier removal, and data clipping with a bounding box.
- `gftin.py`: Processes ground filtering tests. It returns points that pass the ground test and, in debug mode, writes a GeoJSON file exporting the TIN.
- `tin.py`: Creates a TIN (Triangulated Irregular Network) with ground points. This class interfaces with TIN creation and rasterization for any given extent.
- `benchmark.py`: Provides benchmarks for the program. It allows modification of three key parameters in the ground filtering test and outputs statistical results.
- `ptio.py`: Manages input and output operations.
- `geojson.py`: Exports points as a GeoJSON file with specified coordinate transformations, mainly for debugging purposes.
- `pipeline.py`: Utilizes PDAL pipeline to run DBSCAN. This class and its functions let you modify parameters such as `eps` and `min_points` for DBSCAN.
- `vegetation.py`: Extracts tree points from unclassified points. Implementation details are in the report.
- `step3.py`: Main file for step 3.
- `step4.py`: Main file for step 4.
- `step5.py`: Main file for step 5.
