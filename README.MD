<p align="center" style="font-size: 20vw">Aruofier</p>
<p align="center">
    <em>Tiny bot to notify you with loud noise about new advert on Aroudas</em>
</p>

---
## Requirements

[Python 3.10+ ](https://www.python.org/downloads/)

When in cloned repo:
```console
$ python -m pip install -r requirements.txt
```

## Usage
```console
$ python main.py
```

## Settings

Change .env file in the root directory to set up the scrapper

| Variable | Description |
|---|---------------|
|`float` <br/> `default: 0.7` <br/> NOTIFICATION_VOL | How loud sound notification would be. From 0 to 1 |
|`int` <br/> `default: 60` <br/> UPDATE_TIME | Refresh rate in seconds. Try to keep it not too low so cloudflare won't block you |
|`str` <br/> ADS_URL | URL from aruodas with desired filters |
