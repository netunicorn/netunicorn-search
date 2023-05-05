import os
import random
import string

from netunicorn.base import Experiment, Pipeline
from netunicorn.client.remote import RemoteClient
from netunicorn.library.tasks.upload.webdav import UploadToWebDavImplementation
from netunicorn.library.tasks.pcapture import StartCaptureLinuxImplementation, StopAllTCPDumpsLinuxImplementation
from netunicorn.library.tasks.qoe_youtube import WatchYouTubeVideo

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
        .then(WatchYouTubeVideo(
            video_url=task_url,
            duration=DURATION,
            qoe_server_address="redacted",
        ))
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
