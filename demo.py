from dl import M3U8Downloader


def main():
	"""Demo: download Big Buck Bunny test video from https://hls-js.netlify.app/demo/ss"""
	url = 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8'
	dl = M3U8Downloader()
	
	print("Starting download...")
	dl.download_segment(m3u8_url=url)
	dl.convert(video_name='Big Buck Bunny.mp4')
	print('Download complete!')
	input('Press Enter to exit...')


if __name__ == '__main__':
	main()