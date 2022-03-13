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

### Usage
---
1. Import dl module and initialize downloader.
```python
from dl import m3u8downloader
dl = m3u8downloader()
```
2. Use download function to download segments of stream and finally use ffmpeg to concatenate these segments into a mp4 file.
```python
dl.download(stream_url, path_to_save, _ishtz) # automatically choose highest quality
dl.convert('filename.mp4', path_to_save, keep_cache=False)
```
### Attention

- **_ishtz argument is used to skip first 4 bytes of segment to bypass ffmpeg heading check**
- **keep_cache argument is used to keep downloaded segments, it should be deleted after download**
- **parse.py module can be import to parse url hentaiz.cc to m3u8 playlist and then download**