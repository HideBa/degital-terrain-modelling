import json
import pdal

# Define the PDAL pipeline
pipeline_json = {
    "pipeline": [
        {
            "type": "readers.las",
            "filename": "LAS.las"  # Replace with the path to your input LAS file
        },
        {
            "type": "filters.range",
            "limits": "Classification[1:1]"
        },        
        {
            "type": "filters.range",
            "limits": "Intensity[0:900]"  # Filter for intensity values from 0 to 900
        },
        {
            "type": "writers.las",
            "filename": "flatrange_output.las"  # The output file with filtered data
        }
    ]
}

# Create and execute the pipeline
pipeline = pdal.Pipeline(json.dumps(pipeline_json))
pipeline.execute()

print("Intensity filtering complete. Output saved to 'filtered_output.las'")
