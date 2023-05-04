from netunicorn.executor.executor import PipelineExecutor, PipelineExecutorState
from netunicorn.library.tasks.basic import SleepTask
from netunicorn.base.pipeline import Pipeline
from timeit import default_timer as timer

pipeline = Pipeline()
pipeline.report_results = False
for i in range(5):
    pipeline.then([SleepTask(seconds=2), SleepTask(seconds=2), SleepTask(seconds=2), SleepTask(seconds=2)])

ITERS = 10
start = timer()

for _ in range(ITERS):
    executor = PipelineExecutor(
        executor_id="some_id",
        gateway_endpoint="removed",
    )
    executor.pipeline = pipeline
    executor.state = PipelineExecutorState.EXECUTING
    executor()

end = timer()

print((end - start) / ITERS)

# Results:
# so, in total, 0.9sec overhead per stage and approx 0.1 overhead per task
