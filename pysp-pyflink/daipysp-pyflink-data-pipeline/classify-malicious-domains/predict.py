import datatable as dt
from pyflink.table.udf import TableFunction, FunctionContext
# from scoring_h2oai_experiment_abdd7683_e609_11ea_b065_027f1ba7e57a import Scorer as PyScoringPipeline
from scoring_h2oai_experiment_abdd7683_e609_11ea_b065_027f1ba7e57a import Scorer

class DaiPySpTransform(TableFunction):

    def __init__(self):
        self.model = None
        self.in_column_names = None

    def open(self, function_context: FunctionContext):
        """
        Initialization method for the function. It is called before the actual working methods
        and thus suitable for one time setup work.

        :param function_context: the context of the function
        :type function_context: FunctionContext
        """
        self.model = Scorer()
        self.in_column_names = self.model.get_column_names()

    def eval(self, input_data):
        input_list = self.stringToList(input_data)
        pred_list = self.predict(input_list)
        pred_data = self.listToString(pred_list)
        return pred_data

    def stringToList(self, input_data):
        input_dt = dt.Frame(input_data)
        input_df = input_dt.to_pandas()
        # grab the first list since there is only 1 list in the list of lists
        return input_df.values.tolist()[0]

    def predict(self, input_list):
        return self.model.score(input_list)

    def listToString(self, output_list):
        return ','.join(map(str, output_list)) + '\n'
