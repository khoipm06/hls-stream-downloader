## This tool allow you to download hls streaming video

### Installation
---
First, you can clone this repo or download zip archive from github and then extract it.
```bash
git clone https://github.com/phamkhoi06/hls-stream-downloader.git
cd hls-stream-downloader
```

Then, make sure you installed all requirements.

```bash
pip3 install -r requirements.txt
```

Next, check if ffmpeg is in your path

```bash
ffmpeg -version
```

and it should be something like this
> ffmpeg version 5.0.1-tessus  https://evermeet.cx/ffmpeg/  Copyright (c) 2000-2022 the FFmpeg developers
...

If not you can simply download from [ffmpeg's download page](https://ffmpeg.org/download.html)

### Usage
---
1. Import download module and initialize downloader.
```python
from dl import m3u8downloader
dl = m3u8downloader()
```
2. Use download function to download segments of stream and finally use ffmpeg to concatenate these segments into a mp4 file.
```python
# default path_to_save parameter is '.' which mean current folder
dl.download_segment(m3u8_url, path_to_save, _ishtz, quality=-1) # m3u8 url can be gotten in devtools
# quality = -1 means download with highest quality
# or quality can be custom value such as 720, 1080, ... corresponding to 1080x720, 1920x1080, ...
# custom value must be support in video source, if not sure you can leave it blank
dl.convert('filename.mp4', path_to_save, keep_cache=False)
```
### Attention
- **_ishtz argument is used to skip first 4 bytes of segment to bypass ffmpeg heading check**
- **quality argument is used for automating downloads without asking menu, you can leave it blank with or use -1 value for highest quality**
- **keep_cache argument is used to keep downloaded segments, it should be deleted after download**
- **parse module can be imported to parse hentaiz.cc url to m3u8 playlist and then download**
- **parse module can use list.txt (if exist) to download video from hentaiz.cc, sample file is in resources/list.txt**