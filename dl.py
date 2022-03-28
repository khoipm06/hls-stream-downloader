import os
import subprocess
import shutil
import math
from typing import Optional, List
import m3u8
import cloudscraper
from urllib.parse import urljoin


class M3U8Downloader:
	"""A downloader for M3U8 video streams with segment download and conversion capabilities."""
	
	@staticmethod
	def get_context(url: str) -> str:
		"""Fetch the content from a given URL.
		
		Args:
			url: The URL to fetch content from.
			
		Returns:
			The text content of the response.
		"""
		scraper = cloudscraper.create_scraper()
		return scraper.get(url).text
	


	def get_segments_list(self, m3u8_url: str, base_url: Optional[str] = None, q: Optional[int] = None) -> List[str]:
		"""Returns a list of segments given an M3U8 URL and an optional base URL.

		Args:
			m3u8_url: A string representing the M3U8 URL.
			base_url: An optional string representing the base URL.
			q: An optional integer representing the quality of the video.
			
		Returns:
			A list of segment URLs.
		"""
		if base_url is None:
			base_url = m3u8_url[:(m3u8_url.rfind('/') + 1)]
		m3u8_obj = m3u8.loads(self.get_context(m3u8_url))
		# variables used for variant playlists are handled in _select_variant
		
		# If variant playlist, resolve the selected playlist URI (non-interactive or interactive)
		if m3u8_obj.is_variant:
			variant_uri = self._select_variant(m3u8_obj, q=q)
			resolved = urljoin(base_url, variant_uri)
			# Load the selected variant playlist instead of recursing
			m3u8_obj = m3u8.loads(self.get_context(resolved))
		segment_list = m3u8_obj.files or []
		for i, segment in enumerate(segment_list):
			if not segment:
				continue
			if not isinstance(segment, str):
				segment = str(segment)
			if not segment.startswith('http'):  # check if segment url is relative or absolute
				segment_list[i] = urljoin(base_url, segment)
		# Ensure returned list contains strings only
		return [s for s in segment_list if s]

	def _select_variant(self, m3u8_obj, q: Optional[int] = None) -> str:
		"""Select a variant playlist URI from a master M3U8 object.

		This method isolates the logic for choosing which variant to follow.
		If q is provided and matches an available height it will be selected.
		If q == -1, choose the highest available quality.
		Otherwise this will prompt the user interactively.

		Returns:
			The playlist URI (possibly relative) to follow.
		"""
		heights = []
		m3u8_links = {}
		choice_list = ""
		for count, playlist in enumerate(m3u8_obj.playlists):
			res = getattr(playlist.stream_info, 'resolution', None)
			if res:
				width, height = res
			else:
				# fallback when resolution is not available; use bandwidth as a proxy
				width = None
				height = getattr(playlist.stream_info, 'bandwidth', count)
			m3u8_links[height] = playlist.uri
			heights.append(height)
			choice_list += f'{count}. {width if width is not None else "?"}x{height} ~ {height}p\n'

		if q is not None:
			if q in heights:
				return m3u8_links[q]
			elif q == -1:
				return m3u8_links[max(heights)]
			else:
				raise ValueError("Invalid quality option provided")

		# interactive fallback
		print("Press Enter to skip and use the highest quality variant")
		print("Choose a variant to download:")
		print(choice_list, end='')
		choice_input = input("Your choice: ")
		if not choice_input:
			return m3u8_links[max(heights)]
		choice = int(choice_input)
		selected_height = heights[choice]
		print(f'Started downloading {selected_height}p video')
		return m3u8_links[selected_height]


	def download_segment(self, m3u8_url: str, download_dir: str = '.', quality: Optional[int] = None, _iscdn: bool = False) -> None:
		"""Download segments from an M3U8 URL and save them to a specified directory.

		Args:
			m3u8_url: A string representing the M3U8 URL.
			download_dir: An optional string representing the directory to save the segments. 
				Default is the current directory.
			quality: An optional integer representing the desired quality of the video. 
				Use -1 for the highest quality. Default is None.
			_iscdn: An optional boolean used to skip first 4 bytes of segments to bypass ffmpeg heading check.
				Use in case some streams use .html, .png, .jpg,... extension instead of .ts 
				to exploit CDN caching feature. Default is False.
		"""
		cache_dir = os.path.abspath(os.path.join(download_dir, 'vcache'))
		os.makedirs(cache_dir, exist_ok=True)
		print('Getting segments...')
		segment_url_list = self.get_segments_list(m3u8_url, q=quality)
		scraper = cloudscraper.create_scraper()  # instance for downloading segments

		total_segments = len(segment_url_list)
		for i, segment_url in enumerate(segment_url_list, start=1):
			file_name = f'segment-{i}.ts'
			path = os.path.join(cache_dir, file_name)
			percent = math.floor(i / total_segments * 100)
			print(f'[process]: {i}/{total_segments} ~ {percent}%')
			print('[download]:', segment_url)
			print('[target]:', path)
			segment_response = scraper.get(segment_url)
			with open(path, 'wb') as f:
				segment_content = segment_response.content[4:] if _iscdn else segment_response.content
				f.write(segment_content)


	def convert(self, video_name: str, path: str = '.', keep_cache: bool = False) -> None:
		"""Converts the downloaded segments into an MP4 video file.

		Args:
			video_name: A string representing the name of the output video file.
			path: An optional string representing the path where the video file will be saved. 
				Default is the current directory.
			keep_cache: An optional boolean indicating whether to keep the downloaded segments 
				in the cache folder after conversion. Default is False.
		"""
		vcache_dir = os.path.abspath(os.path.join(path, 'vcache'))
		vcache_file = os.path.join(vcache_dir, 'vcache.txt')
		
		if not os.path.exists(vcache_dir):
			print('Video cache directory should exist. Try download_segment method to create it.')
			return
		
		# Write segments list to vcache.txt
		with open(vcache_file, 'w', encoding='utf-8') as lf:
			segment_files = sorted(
				[f for f in os.listdir(vcache_dir) if f.startswith('segment-') and f.endswith('.ts')],
				key=lambda x: int(x.split('-')[1].split('.')[0])
			)
			for segment_file in segment_files:
				file_path = os.path.join(vcache_dir, segment_file)
				if os.path.exists(file_path) and os.path.isfile(file_path):
					lf.write(f'file {file_path}\n')

		try:
			# Combine all segments to mp4 file
			output_path = os.path.abspath(os.path.join(path, video_name))
			subprocess.run(
				["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0", 
				 "-i", vcache_file, "-c", "copy", output_path],
				check=True
			)
			print(f"Video saved to: {output_path}")
		except subprocess.CalledProcessError as e:
			print(f"Failed to execute ffmpeg command: {e}")
		except FileNotFoundError:
			print("ffmpeg not found. Please ensure ffmpeg is installed and in your PATH.")
		
		if keep_cache:
			list_dir = os.listdir(vcache_dir)
			size = sum(
				os.path.getsize(os.path.join(vcache_dir, file))
				for file in list_dir
				if os.path.isfile(os.path.join(vcache_dir, file))
			)
			print(f"vcache folder has {len(list_dir)} files with {size / (1024 * 1024):.2f} MB you may need to remove!")
		else:
			shutil.rmtree(vcache_dir)  # clean left overs