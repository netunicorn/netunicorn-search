from typing import Optional

from netunicorn.base import Minion
from netunicorn.base.task import Task, TaskDispatcher, Result

from multiproblem_experiment.beauty_burst.tasks_definition import watch


class WatchYoutubeLinuxImplementation(Task):
    requirements = [
        "sudo apt-get update",
        "sudo apt-get install -y xvfb wget lsb-release",
        # debian has firefox-esr, ubuntu has firefox
        'if [[ $(lsb_release -is) == "Debian" ]]; then fox_name="firefox-esr"; else fox_name=firefox; fi'
        "sudo apt-get install -y $fox_name",
        "pip3 install selenium pyvirtualdisplay",
        'if [[ $(python3 -c "import platform; print(platform.machine())") == "aarch64" ]]; then carch="-aarch64"; else carch="64"; fi && '
        + 'wget "https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux$carch.tar.gz" -O /tmp/geckodriver.tar.gz',
        "python3 - c 'from webdriver_manager.firefox import GeckoDriverManager; GeckoDriverManager().install()'",
        "wget https://addons.mozilla.org/firefox/downloads/file/4047353/ublock_origin-1.46.0.xpi -O /tmp/ublock_origin.xpi",
    ]

    def __init__(self, url: str, duration: Optional[int] = None, use_xvfb: bool = True):
        self.url = url
        self.duration = duration
        self.use_xvfb = use_xvfb
        super().__init__()

    def run(self) -> Result[str, str]:
        return watch(self.url, self.duration, use_xvfb=self.use_xvfb)


class WatchYoutube(TaskDispatcher):
    def __init__(self, url: str, duration: Optional[int] = None, use_xvfb: bool = True):
        self.url = url
        self.duration = duration
        self.use_xvfb = use_xvfb
        super().__init__()

    def dispatch(self, minion: Minion) -> Task:
        if minion.properties.get("os_family", "").lower() == "linux":
            return WatchYoutubeLinuxImplementation(
                url=self.url, duration=self.duration, use_xvfb=self.use_xvfb
            )

        raise NotImplementedError(
            f"WatchYoutube is not implemented for {minion.properties.get('os_family', '')}"
        )
