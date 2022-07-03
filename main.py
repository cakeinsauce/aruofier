import os
import pathlib
import random
import sys
import threading
import time
from ctypes import POINTER, cast

import bs4
import cloudscraper
import playsound
from comtypes import CLSCTX_ALL, CoInitialize
from dotenv import load_dotenv
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

SOUNDS_DIR = pathlib.Path(__file__).parent.resolve() / "sounds"
SOUND_PATHS = tuple(map(str, SOUNDS_DIR.glob("**/*")))

load_dotenv()

NOTIFICATION_VOL = float(os.getenv("NOTIFICATION_VOL", "0.7"))
UPDATE_TIME = int(os.getenv("UPDATE_TIME", "60"))
ADS_URL = os.environ["ADS_URL"]

scraper = cloudscraper.create_scraper(browser={"custom": "ScraperBot/1.0"})


def play_random_sound(volume: float | None = None) -> None:
    interface = cast(
        AudioUtilities.GetSpeakers().Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        ),
        POINTER(IAudioEndpointVolume),
    )
    previous_volume = interface.GetMasterVolumeLevelScalar()  # type: ignore
    if volume is not None:
        interface.SetMasterVolumeLevelScalar(volume, None)  # type: ignore

    playsound.playsound(random.choice(SOUND_PATHS))

    interface.SetMasterVolumeLevelScalar(previous_volume, None)  # type: ignore


def notify(message: object) -> None:
    print("New ads!")
    print(message)
    play_random_sound(NOTIFICATION_VOL)


def waiting_animation() -> None:
    animation = "|/-\\"
    idx = 0
    while True:
        time.sleep(0.23)
        sys.stdout.write(f"\r{animation[idx % len(animation)]}")
        sys.stdout.flush()
        idx += 1


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
        except TypeError:
            continue
        links.append(link)
    return links


def background_task() -> None:
    print("Starting Aruodas scrapper...")
    threading.Thread(target=waiting_animation).start()
    cache: list[str] = []
    CoInitialize()

    while True:
        links = get_ad_links(get_page_ads(get_page_content(ADS_URL)))
        new_links = tuple(
            l for l in links[: len(links) // 2] if l not in cache
        )

        if cache and new_links:
            notify("\n".join(new_links))
        cache = links

        time.sleep(UPDATE_TIME)


if __name__ == "__main__":
    threading.Thread(target=background_task).start()
