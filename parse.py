import os, json, cloudscraper
from dl import m3u8downloader
from bs4 import BeautifulSoup

def parse_url(link):
	scraper = cloudscraper.create_scraper()
	r = scraper.get(link)
	soup = BeautifulSoup(r.text, features='lxml')
	attribute = soup.select_one('iframe#player').attrs # get player attributes
	url = attribute.get('src')
	title = attribute.get('title')
	spl = 'videoplayback'
	if spl in url:
		# get m3u8 url for older video < 5/2022
		player_url = 'https://apix.gooqlevideo.com/player' + url.split(spl)[1] # get the player url
		r = scraper.get(player_url)
		m3u8_url = json.loads(r.text)['manifest'] # parse m3u8 master url from json
	else:
		# get m3u8 url for newer video > 5/2022
		url = url.split('url=')[-1] # remove iframe prefix
		if url.endswith('mp4'):
			print("Downloading...")
			r = scraper.get(url)
			with open(f'{title}.mp4', 'wb') as f:
				f.write(r.content)
			exit()
		resolution = url.split('/')[-2]
		m3u8_url = url.removesuffix(resolution + '/media.m3u8') + 'master.m3u8' # get m3u8 url
	return title, m3u8_url


def download(link: str, path: str, _ishtz: bool = True, keep_cache: bool = False , quality = None):
	try:
		dl = m3u8downloader() # initialize the downloader
		title, m3u8_url = parse_url(link)
		dl.download_segment(m3u8_url, path, _ishtz=_ishtz, quality=quality) # download the segments
		dl.convert(title + '.mp4', path, keep_cache=keep_cache) #concatenate the segments and convert to mp4 by ffmpeg
	except Exception as e:
		print('An error occurred:', e)

def path():
	path = input('Path to save file: ')
	if not path:
		path = '.' # default path
	return os.path.abspath(path)


if __name__=='__main__':
	filename = 'list.txt' # get link from this file
	if(os.path.exists(filename)):
		save_dir = path()
		with open(filename) as f:
			for link in f:
				download(link, save_dir, quality = -1)
	else:
		link = input('Enter link: ')
		save_dir = path()
		download(link, save_dir)