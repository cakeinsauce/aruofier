import ctypes
import datetime
import os
import pathlib
import random
import shutil
import threading
import time

import bs4
import cloudscraper
import comtypes
import dotenv
import playsound
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

SOUNDS_DIR = pathlib.Path(__file__).parent.resolve() / "sounds"
SOUND_PATHS = tuple(map(str, SOUNDS_DIR.glob("**/*")))

dotenv.load_dotenv()

NOTIFICATION_VOL = float(os.getenv("NOTIFICATION_VOL", "0.7"))
UPDATE_TIME = int(os.getenv("UPDATE_TIME", "60"))
ADS_URL = os.environ["ADS_URL"]

scraper = cloudscraper.create_scraper(browser={"custom": "ScraperBot/1.0"})


def play_random_sound(volume: float | None = None) -> None:
    interface = ctypes.cast(
        AudioUtilities.GetSpeakers().Activate(
            IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None
        ),
        ctypes.POINTER(IAudioEndpointVolume),
    )
    previous_volume = interface.GetMasterVolumeLevelScalar()  # type: ignore
    if volume is not None:
        interface.SetMasterVolumeLevelScalar(volume, None)  # type: ignore

    playsound.playsound(random.choice(SOUND_PATHS))

    interface.SetMasterVolumeLevelScalar(previous_volume, None)  # type: ignore


def print_notification(message: object) -> None:
    now = datetime.datetime.now().strftime("%H:%M:%S")
    terminal_width = shutil.get_terminal_size().columns
    print("\033[92m", f"[{now}]", end="", sep="")
    print("\u001b[36m", "New ads!")
    print("\u001b[0m", message, sep="")
    print("\u001b[31;1m", "─" * (terminal_width - 1), "\u001b[0m", sep="")


def get_page_content(url: str) -> str:
    resp = scraper.get(url=url)
    resp.raise_for_status()
    return resp.text  # type: ignore


def get_page_ads(page_content: str) -> list[bs4.Tag]:
    soup = bs4.BeautifulSoup(page_content, "html.parser")
    return soup.find(class_="list-search").tbody.find_all(  # type: ignore
        class_="list-row", style=False
    )


def get_ad_links(adverts: list[bs4.Tag]) -> list[str]:
    links: list[str] = []
    for advert in adverts:
        try:
            link = advert.td.div.a["href"]
        except (TypeError, AttributeError):
            continue
        links.append(link)
    return links


def main() -> None:
    comtypes.CoInitialize()
    cache: list[str] = []
    while True:
        links = get_ad_links(get_page_ads(get_page_content(ADS_URL)))
        new_links = tuple(
            l for l in links[: len(links) // 2] if l not in cache
        )

        if cache and new_links:
            print_notification("• " + "\n• ".join(new_links))
            play_random_sound(NOTIFICATION_VOL)

        cache = links

        time.sleep(UPDATE_TIME)


if __name__ == "__main__":
    print("Running Aruodas scrapper...")
    threading.Thread(target=main).start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting programm...")
        os._exit(0)
