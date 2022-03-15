import json, os, cloudscraper
from dl import m3u8downloader
from bs4 import BeautifulSoup

def parse_url(link):
	scraper = cloudscraper.create_scraper()
	r = scraper.get(link)
	soup = BeautifulSoup(r.text, features='lxml')
	attribute = soup.select_one('iframe#player').attrs # get player attributes
	url = attribute.get('src')
	title = attribute.get('title')
	player_url = 'https://apix.gooqlevideo.com/player' + url.split('videoplayback')[1] # get the player url
	r = scraper.get(player_url)
	m3u8_url = json.loads(r.text)['manifest'] # parse m3u8 master url from json
	return title, m3u8_url


def download(link: str, path: str, _ishtz: bool = False, keep_cache: bool = False):
	dl = m3u8downloader() # initialize the downloader
	title, m3u8_url = parse_url(link)
	dl.download_segment(m3u8_url, path, _ishtz=True) # download the segments
	dl.convert(title + '.mp4', path, keep_cache=False) #concatenate the segments and convert to mp4 by ffmpeg

def path():
	path = input('Path to save file: ')
	if not path:
		path = '.' # default path
	return os.path.abspath(path)


if __name__=='__main__':
	filename = 'list.txt'
	if(os.path.exists(filename)):
		save_dir = path()
		with open(filename) as f:
			for link in f:
				download(link, save_dir, _ishtz=True)
	else:
		link = input('Enter link: ')
		save_dir = path()
		download(link, save_dir)