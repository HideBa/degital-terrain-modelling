import json

import pdal


class Pipeline:
    """
    A class representing a data processing pipeline.

    Args:
        input_path (str): The path to the input data.
        output_path (str): The path to save the output data.
        output_extra_dims (list, optional): A list of extra dimensions to include in the output data. Defaults to [].

    Attributes:
        pipeline_setting (list): The configuration settings for the pipeline.

    """

    def __init__(self, input_path, output_path, output_extra_dims=[]):
        self.pipeline_setting = self._init_pipeline(
            input_path, output_path, output_extra_dims
        )

    def _init_pipeline(self, input_path, output_path, output_extra_dims=[]):
        """
        Initialize the pipeline with the input and output settings.

        Args:
            input_path (str): The path to the input data.
            output_path (str): The path to save the output data.
            output_extra_dims (list, optional): A list of extra dimensions to include in the output data. Defaults to [].

        Returns:
            list: The initialized pipeline configuration.

        """
        extra_dims = ",".join(output_extra_dims)
        init_pipeline = [
            input_path,
            {
                "type": "writers.las",
                "filename": output_path,
                "extra_dims": extra_dims,
            },
        ]
        return init_pipeline

    def range(self, unclassified_code=1):
        """
        Apply a range filter to the pipeline.

        Args:
            unclassified_code (int, optional): The code representing unclassified points. Defaults to 1.

        Returns:
            Pipeline: The updated pipeline object.

        """
        range_pipe = [
            {
                "type": "filters.range",
                "limits": f"Classification[{unclassified_code}:{unclassified_code}]",
            },
        ]
        # append range_pipe to pipeline_setting as -2 index. This is because the last index is the writer
        self.pipeline_setting = (
            self.pipeline_setting[:-1] + range_pipe + self.pipeline_setting[-1:]
        )
        return self

    def dbscan(self, min_points=6, eps=3):
        """
        Apply a DBSCAN filter to the pipeline.

        Args:
            min_points (int, optional): The minimum number of points in a cluster. Defaults to 6.
            eps (int, optional): The maximum distance between points in a cluster. Defaults to 3.

        Returns:
            Pipeline: The updated pipeline object.

        """
        dbscan_pipe = [
            {
                "type": "filters.dbscan",
                "min_points": min_points,
                "eps": eps,
                "dimensions": "X,Y,Z",
            },
            {
                "type": "filters.expression",
                "expression": "ClusterID != -1",
            },
        ]
        # append dbscan_pipe to pipeline_setting as -2 index. This is because the last index is the writer
        self.pipeline_setting = (
            self.pipeline_setting[:-1] + dbscan_pipe + self.pipeline_setting[-1:]
        )
        return self

    def execute(self):
        """
        Execute the pipeline.

        Returns:
            int: The number of points processed by the pipeline.

        """
        print("Executing pipeline...")
        print("Pipeline: ", self.pipeline_setting)
        pipeline_json = json.dumps(self.pipeline_setting)
        print("Pipeline json: ", pipeline_json)
        pipeline = pdal.Pipeline(pipeline_json)
        count = pipeline.execute()
        arrays = pipeline.arrays
        metadata = pipeline.metadata
        log = pipeline.log

        print("Pipeline executed successfully")
        print("Point count: ", count)
        # print("Arrays: ", arrays)
        # print("Metadata: ", metadata)
