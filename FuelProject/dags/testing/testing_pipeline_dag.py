import unittest
import datetime

from airflow.models import DagBag

# create testing class
class PostgresDAG(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dagbag = DagBag()

    def setUp(self):
        # get the DAG and some tasks
        self.dag = self.dagbag.get_dag(dag_id="dag_train_evaluation_pipeline")
        self.dag_train_task = self.dag.get_task('train_dnn')
        self.dag__eval_task = self.dag.get_task('evaluation')
        self.dag_save_metadata_task = self.dag.get_task('save_evaluation_metadata')

    def test_dag_loaded(self):
        # check for import errors, the number of tasks and is the dag exists
        self.assertDictEqual(self.dagbag.import_errors, {})  
        # check to see if the dag is not none
        self.assertIsNotNone(self.dag)
        # check the number of tasks
        self.assertEqual(len(self.dag.tasks), 9)
        # check to see if the email mathces
        self.assertEqual(self.dag.email, 'apeter@yahoo.com')
        # check to see if the retry delay is the same
        self.assertEqual(self.dag.retry_delay, datetime.timedelta(minutes = 5))

    def test_training_process(self):
        self.assertEqual(self.dag_train_task.task_id, 'train_dnn')
        self.assertEqual(self.dag_train_task.owner, 'Alex')

    def test_evaulation_process(self):
        self.assertEqual(self.dag__eval_task.task_id, 'evaluation')
        self.assertEqual(self.dag__eval_task.owner, 'Alex')
    
    def test_evluation_metadata_trigger(self):
        self.assertEqual(self.dag_save_metadata_task.task_id, 'save_evaluation_metadata')

if __name__ == '__main__':
    unittest.main()