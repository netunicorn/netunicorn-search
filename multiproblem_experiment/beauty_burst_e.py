import os
import random
import string
import cloudpickle

from netunicorn.base.experiment import Experiment
from netunicorn.base.pipeline import Pipeline
from netunicorn.library.tasks.upload.webdav import UploadToWebDavImplementation
from netunicorn.client.remote import RemoteClient
from netunicorn.library.tasks.pcapture import StartCaptureLinuxImplementation, StopAllTCPDumpsLinuxImplementation

import beauty_burst.tasks_definition as tasks_definition
import beauty_burst

cloudpickle.register_pickle_by_value(tasks_definition)
cloudpickle.register_pickle_by_value(beauty_burst)

pipeline = Pipeline()
pipeline.environment_definition.image = "redacted"

video_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=mghhLqu31cQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",
    "https://www.youtube.com/watch?v=q9Mnm0jbw88",
    "https://www.youtube.com/watch?v=oHNKTlz1lps",
]
DURATION = 30

video_tasks = []
for i in range(10):
    for url in video_urls:
        random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        youtube_id = url.split('=')[-1]
        name = f"{youtube_id}-{random_id}"
        video_tasks.append((name, url))

for task_name, task_url in video_tasks:
    (
        pipeline
        .then(StartCaptureLinuxImplementation(task_name))
        .then(beauty_burst.WatchYoutubeLinuxImplementation(url=task_url, duration=DURATION))
        .then(StopAllTCPDumpsLinuxImplementation())
    )

pipeline.then(UploadToWebDavImplementation(
    filepaths={x[0] for x in video_tasks},
    endpoint=os.environ['UPLOAD_ENDPOINT'],
    username=os.environ['WEBDAV_LOGIN'],
    password=os.environ['WEBDAV_PASSWORD']
))
print(len(pipeline.tasks))

client = RemoteClient(
    endpoint=os.environ['UNICORN_ENDPOINT'],
    login=os.environ['UNICORN_LOGIN'],
    password=os.environ['UNICORN_PASSWORD']
)

minion_pool = client.get_nodes().filter(lambda x: x['kernel'] == 'Linux')

experiment = Experiment().map(pipeline, minion_pool.take(10))
experiment.keep_alive_timeout_minutes = 200

experiment_label = "beauty-burst-1.0"
client.prepare_experiment(experiment, experiment_label)
# sleep before starting execution
client.start_execution(experiment_label)
