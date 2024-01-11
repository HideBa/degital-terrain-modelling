import json
import pdal
import numpy as np

# Define the PDAL pipeline to read LAS file and compute statistics
stats_pipeline_json = {
    "pipeline": [
        {
            "type": "readers.las",
            "filename": "LAS.las"
        },
        {
            "type": "filters.stats",
            "dimensions": "Intensity"
        }
    ]
}

# Create and execute the pipeline for statistics
stats_pipeline = pdal.Pipeline(json.dumps(stats_pipeline_json))
stats_pipeline.execute()

# Extract the statistics
stats = stats_pipeline.metadata["metadata"]["filters.stats"]["statistic"]
intensity_stats = next(item for item in stats if item["name"] == "Intensity")

# Calculate the 66th percentile
min_intensity = intensity_stats["minimum"]
max_intensity = intensity_stats["maximum"]
percentile_35_intensity = np.percentile(range(int(min_intensity), int(max_intensity) + 1), 35)

# Define the main PDAL pipeline with the calculated intensity limit
main_pipeline_json = {
    "pipeline": [
        {
            "type": "readers.las",
            "filename": "LAS.las"
        },
        {
            "type": "filters.range",
            "limits": "Classification[1:1]"
        },
        {
            "type": "filters.range",
            "limits": f"Intensity[0:{percentile_35_intensity}]"
        },
        {
            "type": "writers.las",
            "filename": "vegetation_output35.las"
        }
    ]
}

# Create and execute the main pipeline
main_pipeline = pdal.Pipeline(json.dumps(main_pipeline_json))
main_pipeline.execute()

print(f"Vegetation extraction complete. Output saved to 'vegetation_output.las'. Intensity filter applied up to {percentile_35_intensity}.")
