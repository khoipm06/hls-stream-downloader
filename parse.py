import os
from typing import Tuple, Optional
import cloudscraper
from bs4 import BeautifulSoup

from dl import M3U8Downloader


def parse_url(link: str) -> Tuple[str, str]:
	"""Parse a video URL to extract the title and M3U8 URL.
	
	Args:
		link: The URL of the video page.
		
	Returns:
		A tuple containing (title, m3u8_url).
		
	Raises:
		AttributeError: If the page structure doesn't match expected format.
		KeyError: If the API response doesn't contain expected keys.
	"""
	scraper = cloudscraper.create_scraper()
	response = scraper.get(link)
	soup = BeautifulSoup(response.content, features='lxml')
	
	iframe = soup.find('iframe')
	if not iframe:
		raise ValueError("No iframe found in the page")
	
	src = iframe.get('src')
	if not src:
		raise ValueError("Iframe has no src attribute")
	
	video_id = src[src.rfind('/') + 1:]
	api_url = f'https://ipa.sonar-cdn.com/play/{video_id}'
	json_obj = scraper.get(api_url).json()
	
	title: str = json_obj['title']
	m3u8_url = json_obj['hls'][0]['url']
	
	# Post-processing title
	if title.endswith('.mp4'):
		title = title.removesuffix('.mp4')

	# OLD METHOD
	# spl = 'videoplayback'
	# if spl in url:
	# 	# get m3u8 url for older video < 5/2022
	# 	player_url = 'https://apix.gooqlevideo.com/player' + url.split(spl)[1] # get the player url
	# 	r = scraper.get(player_url)
	# 	m3u8_url = json.loads(r.text)['manifest'] # parse m3u8 master url from json
	# else:
	# 	# get m3u8 url for newer video > 5/2022
	# 	url = url.split('url=')[-1] # remove iframe prefix
	# 	if url.endswith('mp4'):
	# 		print("Downloading...")
	# 		r = scraper.get(url)
	# 		with open(f'{title}.mp4', 'wb') as f:
	# 			f.write(r.content)
	# 		exit()
	# 	resolution = url.split('/')[-2]
	# 	m3u8_url = url.removesuffix(resolution + '/media.m3u8') + 'master.m3u8' # get m3u8 url
 
	return title, m3u8_url


def download(link: str, path: str, keep_cache: bool = False, quality: Optional[int] = None) -> None:
	"""Download a video from the given link.
	
	Args:
		link: The URL of the video page.
		path: The directory path to save the video.
		keep_cache: Whether to keep the cache folder after conversion. Default is False.
		quality: The desired quality of the video. Use -1 for the highest quality. Default is None.
	"""
	try:
		dl = M3U8Downloader()  # initialize the downloader
		title, m3u8_url = parse_url(link)
		print(f"Downloading: {title}")
		dl.download_segment(m3u8_url, path, quality=quality)  # download the segments
		dl.convert(f'{title}.mp4', path, keep_cache=keep_cache)  # concatenate and convert to mp4
		print(f"Successfully downloaded: {title}")
	except Exception as e:
		print(f'An error occurred while downloading {link}: {e}')


def get_save_path() -> str:
	"""Prompt user for save path and return the absolute path.
	
	Returns:
		The absolute path where files should be saved.
	"""
	path = input('Path to save file (press Enter for current directory): ').strip()
	if not path:
		path = '.'  # default path
	return os.path.abspath(path)


if __name__ == '__main__':
	filename = 'list.txt'  # get link from this file
	if os.path.exists(filename):
		save_dir = get_save_path()
		with open(filename, 'r', encoding='utf-8') as f:
			links = [line.strip() for line in f if line.strip()]
			print(f"Found {len(links)} links to download")
			for idx, link in enumerate(links, start=1):
				print(f"\n[{idx}/{len(links)}] Processing: {link}")
				download(link, save_dir, quality=-1)
	else:
		link = input('Enter video url: ').strip()
		if not link:
			print("No URL provided. Exiting.")
		else:
			save_dir = get_save_path()
			download(link, save_dir)