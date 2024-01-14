import json
import pdal
import numpy as np

# Read the LAS file and extract intensity data
reader_json = {
    "pipeline": [
        {
            "type": "readers.las",
            "filename": "testlaz.LAZ"
        },
                {
            "type": "filters.range",
            "limits": "Classification[1:1]"
        },
        {
            "type": "filters.stats",
            "dimensions": "Intensity"
        }
    ]
}

reader_pipeline = pdal.Pipeline(json.dumps(reader_json))
reader_pipeline.execute()

# Extract intensity data
arrays = reader_pipeline.arrays[0]
intensity = arrays['Intensity']

# Calculate mean and standard deviation
mean_intensity = np.mean(intensity)
std_intensity = np.std(intensity)

# Apply Z-score normalization
normalized_intensity = (intensity - mean_intensity) / std_intensity

# Filter the data based on normalized intensity
filtered_indices = np.where((normalized_intensity >= -2) & (normalized_intensity <= 1))[0]
filtered_arrays = arrays[filtered_indices]

# Create a new LAS file with the filtered data
writer_json = {
    "pipeline": [
        {
            "type": "writers.las",
            "filename": "normalized_outputzscore.las"
        }
    ]
}

writer_pipeline = pdal.Pipeline(json.dumps(writer_json), arrays=[filtered_arrays])
writer_pipeline.execute()

print("Z-score normalization and filtering complete. Output saved to 'normalized_outputzscore.las'")
