from dl import m3u8downloader

# Demo download big buck bunny test video from https://hls-js.netlify.app/demo/ss
url = 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8'
dl = m3u8downloader()
dl.download_segment(m3u8_url = url)
dl.convert(video_name = 'Big Buck Bunny.mp4')
print('Download complete...')
input()