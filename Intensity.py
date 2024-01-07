import json
import pdal

# Define the PDAL pipeline
# Replace 'your_file.las' with the path to your LAS file
pipeline_json = {
    "pipeline": [
        {
            "type": "readers.las",
            "filename": "LAS.las"
        },
        # Filter by intensity values
        {
            "type": "filters.range",
            "limits": "Intensity[0:900]"  
        },
        # Write to a new LAS file
        {
            "type": "writers.las",
            "filename": "vegetation_output.las"
        }
    ]
}

# Execute the pipeline
pipeline = pdal.Pipeline(json.dumps(pipeline_json))
pipeline.execute()

print("Vegetation extraction complete. Output saved to 'vegetation_output.las'")
