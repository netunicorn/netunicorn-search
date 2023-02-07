from netunicorn.base import Task


class BenignTask(Task):
    def __init__(self, url1, url2):
        self.url1 = url1
        self.url2 = url2
        super().__init__()

    def run(self):
        import subprocess

        for i in range(500):
            subprocess.check_output(f"curl {self.url1}", shell=True)
            subprocess.check_output(f"curl {self.url2}", shell=True)
        return 0
