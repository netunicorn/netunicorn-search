import os

import cloudpickle

from netunicorn.base.experiment import Experiment
from netunicorn.base.pipeline import Pipeline
from netunicorn.client.remote import RemoteClient

from .letsencrypt import LetsEncryptDNS01Validation

cloudpickle.register_pickle_by_value(LetsEncryptDNS01Validation)
validation_pipeline = Pipeline([
    LetsEncryptDNS01Validation(
        domain="redacted",
        token="redacted"
    )
])

client = RemoteClient(
    endpoint=os.environ['UNICORN_ENDPOINT'],
    login=os.environ['UNICORN_LOGIN'],
    password=os.environ['UNICORN_PASSWORD']
)

minion_pool = client.get_minion_pool()

experiment = Experiment().map(validation_pipeline, minion_pool)

experiment_label = 'letsencrypt_validate_dns_0.0.1'
client.prepare_experiment(experiment, experiment_label)
client.start_execution(experiment_label)
