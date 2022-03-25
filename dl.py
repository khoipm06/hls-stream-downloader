import os
import subprocess
import shutil
import math
import m3u8
import cloudscraper
from urllib.parse import urljoin

class m3u8downloader:
	
	@staticmethod
	def get_context(url: str):
		scraper = cloudscraper.create_scraper()
		return scraper.get(url).text
	


	def get_segments_list(self, m3u8_url: str, base_url: str = None, q: int = None) -> list:
		"""
		Returns a list of segments given an M3U8 URL and an optional base URL.

		:param m3u8_url: A string representing the M3U8 URL.
		:param base_url: An optional string representing the base URL.
		:param q: An optional integer representing the quality of the video.
		:return: A list of segment URLs.
		"""
		base_url = m3u8_url[:(m3u8_url.rfind('/')+1)]
		m3u8_obj = m3u8.loads(self.get_context(m3u8_url))
		h = list()
		m3u8_links = dict()
		if m3u8_obj.is_variant:
			print("Enter to skip and use the highest quality variant")
			print("Choose a variant to download: ")
			for count, playlist in enumerate(m3u8_obj.playlists):
				weight, height = playlist.stream_info.resolution
				h.append(height)
				m3u8_links[height] = playlist.uri
				print(f'{count}. {weight}x{height} ~ {height}p')
			if q:
				if q in h:
					choice = h.index(q)
				elif q == -1:
					choice = ''
				else:
					raise ValueError("Invalid quality option provided.")
			else:
				choice = input("Your choice: ")
			if not choice:
				m3u8_link = m3u8_links[max(h)]
			else:
				m3u8_link = m3u8_links.get(h[int(choice)])
			return self.get_segments_list(urljoin(base_url, m3u8_link), base_url)
		segment_list = m3u8_obj.files
		for i in range(len(segment_list)):
			segment = segment_list[i]
			if not segment.startswith('http'): # check if segment url is relative or absolute
				segment_list[i] = urljoin(base_url, segment)
		return segment_list


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
		cache_dir = os.path.join(download_dir, 'vcache')
		os.makedirs(cache_dir ,exist_ok=True)
		print('Getting segments...')
		segment_url_list = self.get_segments_list(m3u8_url, q=quality)
		scraper = cloudscraper.create_scraper() # instance for download segments

		l = len(segment_url_list)
		for i, segment_url in enumerate(segment_url_list, start=1):
			file_name = 'segment-%s.ts' % i
			path = '%s/%s' % (cache_dir, file_name)
			percent_ =  math.floor(i/l*100)
			print(f'[process]: {i}/{l} ~ {percent_}%')
			print('[download]: ', segment_url)
			print('[target]: ', path)
			segment_context = scraper.get(segment_url)
			with open(path, 'wb') as f:
				segment_content = segment_context.content[4:] if _iscdn else segment_context.content
				f.write(segment_content)


	def convert(self, video_name: str, path: str = '.', keep_cache: bool = False):
		"""
		Converts the downloaded segments into an MP4 video file.

		:param video_name: A string representing the name of the output video file.
		:param path: An optional string representing the path where the video file will be saved. Default is the current directory.
		:param keep_cache: An optional boolean indicating whether to keep the downloaded segments in the cache folder after conversion. Default is False.
		:return: None
		"""
		os.makedirs(path ,exist_ok=True)
		vcache_dir = os.path.join(path, 'vcache')
		os.chdir(vcache_dir)
		with open('vcache.txt', 'w') as lf:
			i = 0
			for i in range(len(os.listdir())):
				file_name =  f'segment-{i}.ts'
				if os.path.exists(file_name) and os.path.isfile(file_name):
					lf.write(f'file {file_name}\n') # write segments list to vcache.txt
				i += 1

		try:
			# combine all segments to mp4 file
			subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "vcache.txt", "-c", "copy", f"../{video_name}"], check=True)
		except ChildProcessError:
			print("Failed to execute ffmpeg command")
		if keep_cache:
			list_dir = os.listdir('.')
			size = sum(os.path.getsize(f) for f in list_dir if os.path.isfile(f))
			print("vcache folder has %i files with %i MB you may need to remove!" % (len(list_dir), size/(1024*1024)))
		else:
			os.chdir('..')
			shutil.rmtree('vcache') # clean left overs