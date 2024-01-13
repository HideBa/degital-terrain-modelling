import json
import pdal


class Pipeline:
    def __init__(self, input_path, output_path, output_extra_dims=[]):
        self.pipeline_setting = self._init_pipeline(
            input_path, output_path, output_extra_dims
        )

    def _init_pipeline(self, input_path, output_path, output_extra_dims=[]):
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
