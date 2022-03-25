
# hls-stream-downloader

## Overview

`This code snippet is a tool for downloading HLS streaming videos. It provides an easy and convenient way for downloading and converting video segments into an MP4 file using FFmpeg.`

---

##  Getting Started

**System Requirements:**

* **Python**: `version 3.x`
* **Ffmpeg**

**Python modules**

* **m3u8**
* **cloudscraper**
* **beautifulsoup4**
* **lxml**

### Installation

First, you can clone this repo or download zip archive from github and then extract it.

```bash
git clone https://github.com/phamkhoi06/hls-stream-downloader.git
cd hls-stream-downloader
```

Then, create a virtual enviroment for python to isolate project(recommend) or skip to install system-wide
```bash
python3 -m venv .venv
# Then make sure to activate it
# For Linux
source .venv/bin/activate
# For Windows
# CMD
.venv\Scripts\activate.bat
#PowerShell
.venv\Scripts\Activate.ps1
```
After that, install all requirements
```bash
pip3 install -r requirements.txt
```

Next, check if ffmpeg is in your path

```bash
ffmpeg -version
```

and it should be something like this

> ffmpeg version 5.0.1-tessus https://evermeet.cx/ffmpeg/ Copyright (c) 2000-2022 the FFmpeg developers
> ...

If not you can simply download from [ffmpeg's download page](https://ffmpeg.org/download.html) then extract it and add excutable file to PATH variable. Or you can use package manager to simplify process
* Ubuntu/Debian
```
sudo apt-get install ffmpeg
```
* CentOS/Fedora/RHEL
```
sudo dnf install ffmpeg
```

* Arch Linux
```
sudo pacman -S ffmpeg
```

---

### Usage

1. Import download module and initialize downloader.

```python
from dl import m3u8downloader
dl = m3u8downloader()
```

2. Use download function to download segments of stream and finally use ffmpeg to concatenate these segments into a mp4 file or any formats that ffmpeg supports such as m4v, mkv, avi,... and many others

```python
# default path_to_save parameter is '.' which mean current working folder
dl.download_segment(m3u8_url, path_to_save, _iscdn, quality=-1) # m3u8 url can be gotten in devtools
# quality = -1 means download with highest quality
# or quality can be custom value such as 720, 1080, ... corresponding to 1080x720, 1920x1080, ...
# custom value must be available in video source, if not sure you can leave it blank
dl.convert('output_filename.mp4', path_to_save, keep_cache=False)
```
You can try [demo file](demo.py)

---

## Prototype

Summary all main functionality in [download module](dl.py)
```python
def get_segments_list(self, m3u8_url: str, base_url: str = None, q: int = None) -> list:
	"""
	Returns a list of segments given an M3U8 URL and an optional base URL.

	:param m3u8_url: A string representing the M3U8 URL.
	:param base_url: An optional string representing the base URL.
	:param q: An optional integer representing the quality of the video.
	:return: A list of segment URLs.
	"""
def download_segment(self, m3u8_url: str, download_dir: str = '.', quality = None, _iscdn: bool = False):
	"""
	Download segments from an M3U8 URL and save them to a specified directory.

	:param m3u8_url: A string representing the M3U8 URL.
	:param download_dir: An optional string representing the directory to save the segments. Default is the current directory.
	:param quality: An optional integer representing the desired quality of the video. Use -1 for the highest quality. Default is None.
	:param _iscdn: An optional boolean use to skip first 4 bytes of segments to bypass ffmpeg heading check.
	Use in case some stream use .html, .png, .jpg,... extension instead of .ts to exploit CDN caching feature. Default is False.
	:return: None
	"""
def convert(self, video_name: str, path: str = '.', keep_cache: bool = False):
	"""
	Converts the downloaded segments into an MP4 video file.

	:param video_name: A string representing the name of the output video file.
	:param path: An optional string representing the path where the video file will be saved. Default is the current directory.
	:param keep_cache: An optional boolean indicating whether to keep the downloaded segments in the cache folder after conversion. Default is False.
	:return: None
	"""
```