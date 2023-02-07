import time

from datetime import datetime

from netunicorn.base import Task
from netunicorn.base.experiment import Experiment, ExperimentStatus
from netunicorn.base.pipeline import Pipeline
from netunicorn.client.remote import RemoteClient


class CustomSleepTask(Task):
    # to make system build an image with some dependencies inside
    requirements = [
        "pip3 install pandas numpy matplotlib",
        "apt install -y byobu",
    ]

    def __init__(self, seconds: int):
        self.seconds = seconds
        super().__init__()

    def run(self):
        time.sleep(self.seconds)
        return self.seconds


pipeline = Pipeline(tasks=[CustomSleepTask(seconds=5)])
experiment = Experiment()
client = RemoteClient(
    endpoint="<endpoint>",
    login="<login>",
    password="<password>",
)
pool = client.get_minion_pool().take(20)
print(f"Pool length: {len(pool)}")
experiment.map(pool, pipeline)

label = "aabb-all-1.0.23"
print(f"Send experiment preparation request, {datetime.now()}")
client.prepare_experiment(experiment, label)

while True:
    time.sleep(1)
    status = client.get_experiment_status(label).status
    if status == ExperimentStatus.READY:
        break

print(f"Experiment prepared, starting {datetime.now()}")

client.start_execution(label)

while True:
    time.sleep(1)
    status = client.get_experiment_status(label).status
    if status == ExperimentStatus.FINISHED:
        break

print(f"Experiment finished, {datetime.now()}")


"""
---------------------------------------------------------
SaltStack, pipeline -- single task to sleep 5 seconds
1 minion:

start: 6:39:57
docker compilation start: 6:39:58
docker compilation end: 6:41:53
distribution start: 6:41:54
distribution ends: 6:42:06
status READY: 6:42:07


Total time for experiment preparation: 130 seconds
docker compilation: 115 seconds
image distribution: 12 seconds
platform overhead: 3 seconds

Total time for experiment execution: 8.5 seconds
Task - sleep 5 seconds
3.5 seconds - overhead of the platform + executor

---------------------------------------------------------

10 minions:

start: 07:04:59
docker compilation start: 07:04:59
docker compilation end: 07:05:57
distribution start: 07:06:00
distribution ends: 07:06:08
status READY, starting: 07:06:10
experiment finished: 07:06:28

Total time for experiment preparation: 70 seconds
docker compilation: 58 seconds
image distribution: 8 seconds
platform overhead: 4 seconds

Total time for experiment execution: 18 seconds
Task - sleep 5 seconds
13 seconds - overhead of the platform + executor

---------------------------------------------------------

20 minions:

start: 07:18:26
docker compilation start: 07:18:26
docker compilation end: 07:19:07
distribution start: 07:19:11
distribution ends: 07:19:43
status READY, starting: 07:19:44
experiment finished: 07:20:08

Total time for experiment preparation: 76 seconds
docker compilation: 41 seconds
image distribution: 32 seconds
platform overhead: 3 seconds

Total time for experiment execution: 24 seconds
Task - sleep 5 seconds
19 seconds - overhead of the platform + executor

---------------------------------------------------------
Azure Containers, pipeline -- single task to sleep 5 seconds
1 minion:

start: 19:28:55
docker compilation start: 19:28:55
docker compilation end: 19:29:47
distribution start: 19:29:51
distribution ends: 19:29:51     # no distribution, discuss later
status READY: 19:29:52
experiment finished: 11:30:28


Total time for experiment preparation: 57 seconds
docker compilation: 52 seconds
image distribution: 0 seconds
platform overhead: 5 seconds

Total time for experiment execution: 36 seconds
Task - sleep 5 seconds
31 seconds - overhead of the platform + executor + ! image distribution !

---------------------------------------------------------

10 minions:

start: 21:07:22
docker compilation start: 21:07:22
docker compilation end: 21:08:40
distribution start: 21:08:43
distribution ends: 21:08:43
status READY: 21:08:44
experiment finished: 21:09:36


Total time for experiment preparation: 82 seconds
docker compilation: 78 seconds
image distribution: 0 seconds
platform overhead: 4 seconds

Total time for experiment execution: 52 seconds
Task - sleep 5 seconds
47 seconds - overhead of the platform + executor + ! image distribution !

---------------------------------------------------------

20 minions -- cannot conduct the experiment,
because quota (10 cores in total for a region) is exceeded
update: increased the quota and remeasured

Total time for experiment preparation: 116 seconds
docker compilation: 12 seconds
image distribution: 0 seconds
platform overhead: 4 seconds

Total time for experiment execution: 54 seconds
Task - sleep 5 seconds
49 seconds - overhead of the platform + executor + ! image distribution !

---------------------------------------------------------

Server side memory (all measure as resident memory)
 - saltstack infrastructure connector = 71mb
 - azure containers infrastructure connector = 63mb
 - gateway = 57mb
 - processor = 72mb
 - mediator = 71mb
 - compilation = 42mb
 - authentication = 41mb
 - postgres = 208mb
"""
