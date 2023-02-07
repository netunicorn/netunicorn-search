from typing import Optional


from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from netunicorn.base.task import Result, Success, Failure
from enum import IntEnum


class VideoStatus(IntEnum):
    UNSTARTED = -1
    ENDED = 0
    PLAYING = 1
    PAUSED = 2
    BUFFERING = 3
    CUED = 5




def watch(
    url: str, duration: Optional[int] = None, use_xvfb: bool = True
) -> Result[str, str]:
    if isinstance(duration, int) and duration <= 0:
        return Failure(f"Video duration must be positive, provided: {duration} seconds")

    # start firefox with xvfb
    display = None
    if use_xvfb:
        display = Display(visible=False, size=(1920, 1080))
        display.start()
    driver = webdriver.Firefox()
    driver.install_addon("/tmp/ublock_origin.xpi", temporary=True)

    # open url and wait for video player to load
    driver.get(url)
    time.sleep(
        5
    )  # ublock often reloads the page once to remove video ads, so let's wait
    video = driver.find_element(By.ID, "movie_player")
    if video is None:
        return Failure(f"Video player not found on the given page: {url}")

    video.click()
    if duration is not None:
        time.sleep(duration)
        result = Success(f"Finished watching video after {duration} seconds")
    else:
        result = None
        player_status = VideoStatus.PLAYING
        while player_status in {VideoStatus.PLAYING, VideoStatus.BUFFERING}:
            time.sleep(1)
            player_status = driver.execute_script(
                "return document.getElementById('movie_player').getPlayerState()"
            )
            try:
                player_status = VideoStatus(player_status)
            except ValueError:
                result = Failure(f"Unknown player status: {player_status}")
                break

        if result is None:
            Success(f"Finished watching video with status: {player_status.name}")

    driver.quit()
    if use_xvfb:
        display.stop()
    return result


if __name__ == "__main__":
    print(
        watch(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            duration=None,
            use_xvfb=False,
        )
    )
