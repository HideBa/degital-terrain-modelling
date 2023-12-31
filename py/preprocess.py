import pdal


def remove_outliers(input_path, output_path, nb_neighbors=10, std_ratio=2.0):
    """
    Remove outliers from a point cloud file
    """
    pipeline_setting = """
    [
        "{input}",
        {{
            "type": "filters.outlier",
            "method": "statistical",
            "mean_k": {nb_neighbors},
            "multiplier": {std_ratio}
        }},
        "{output}"
    ]
    """.format(
        input=input_path,
        output=output_path,
        nb_neighbors=nb_neighbors,
        std_ratio=std_ratio,
    )
    print("setting", pipeline_setting)
    pipeline = pdal.Pipeline(pipeline_setting)
    count = pipeline.execute()
    arrays = pipeline.arrays
    metadata = pipeline.metadata
    log = pipeline.log
    print("Pipeline executed successfully")
    print("Point count: ", count)
    print("Arrays: ", arrays)
    print("Metadata: ", metadata)
    print("Log: ", log)
