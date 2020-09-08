import glob
import logging
import os
import shutil
import sys
import tempfile

import pandas as pd
from pathlib import Path

from predict import DaiPySpTransform
from pyflink.table.udf import udtf
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, TableConfig, DataTypes

# from scoring_h2oai_experiment_abdd7683_e609_11ea_b065_027f1ba7e57a import Scorer as PyScoringPipeline

from scoring_h2oai_experiment_abdd7683_e609_11ea_b065_027f1ba7e57a import Scorer

class RealTimePredMalDomains():

    def __init__(self):
        self.home = str(Path.home())
        self.pipeline()

    def pipeline(self):
        # Create Execution Environment
        env = StreamExecutionEnvironment.get_execution_environment()
        env.set_parallelism(1)
        t_config = TableConfig()
        t_env = StreamTableEnvironment.create(env, t_config)

        ##
        # Get Predicted Header
        ##
        model = Scorer()
        out_column_names = model.get_target_labels()
        out_md_df_header = pd.DataFrame(out_column_names)
        out_md_table_header = t_env.from_pandas(out_md_df_header)

        ##
        # Get Real Time Data
        ##

        # Registers a source Table named maliciousDomainsSource
        # example.py passes in list of domains to be scored since type is the label
        path_to_md_data = self.home + "/daipysp-pyflink/test-data/test-real-time-data/test_*.csv"
        # Load in csv data to Pandas DataFrame
        md_csv_df = pd.concat([pd.read_csv(f) for f in glob.glob(path_to_md_data)], ignore_index=True)
        # Create PyFlink Table from Pandas DataFrame
        md_table = t_env.from_pandas(md_csv_df,
                                     DataTypes.ROW([DataTypes.FIELD("domain", DataTypes.STRING())]))

        ##
        # Predict Real Time Data
        ##

        # configure the off-heap memory of current taskmanager to enable the python worker uses off-heap memory.
        t_env.get_config().get_configuration().set_string("taskmanager.memory.task.off-heap.size", '80m')
        # Register the Python Table User Defined Function
        t_env.register_function("daiPySpTransform", udtf(DaiPySpTransform(), DataTypes.STRING(),
                                                         DataTypes.STRING()))
        pred_md_table = md_table.select('daiPySpTransform(domain)')

        # Prepend Pred Header
        out_md_table = out_md_table_header.union(pred_md_table)

        ##
        # Print Real-Time Scores
        ##

        # Registers a sink Table named malDomPredSink
        path_to_mdpred_data = self.home + "/daipysp-pyflink/pred-data/pred-real-time-data/pred_md_data.csv"
        malicious_domains_pred_sink_ddl = """
            create table malDomPredSink (
                type.generated DOUBLE,
                type.non-generated DOUBLE
            ) with (
                'connector.type' = 'filesystem',
                'format.type' = 'csv',
                'connector.path' = '%s'
            )
        """ % path_to_mdpred_data
        t_env.execute_sql(malicious_domains_pred_sink_ddl)

        out_md_table = out_md_table.execute_insert("malDomPredSink")

        # Execute Flink Table Streaming Data Pipeline Job
        out_md_table.execute("Deploy DAI Python SP within a PyFlink Streaming Pipeline")


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

    RealTimePredMalDomains()
