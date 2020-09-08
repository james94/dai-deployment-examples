from pathlib import Path

from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from scoring_h2oai_experiment_abdd7683_e609_11ea_b065_027f1ba7e57a import Scorer

class BeamStreamPredMalDomains():

    def __init__(self):
        options = PipelineOptions()
        options.view_as(StandardOptions).runner = 'FlinkRunner'
        options.view_as(StandardOptions).flink_master = 'localhost:8081'
        options.view_as(StandardOptions).environment_type = 'LOOPBACK'
        self.pipeline = beam.Pipeline(options=options)
        self.home = str(Path.home())
        self.pipeline()

    def beamStreamPipeline(self):

        ##
        # Get Real Time Data
        ##

        # Registers a source Table named maliciousDomainsSource
        # example.py passes in list of domains to be scored since type is the label
        path_to_md_data = self.home + "/daipysp-pyflink/test-data/test-real-time-data/test_*.csv"
        lines = self.pipeline | ReadFromText()