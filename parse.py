import json, cloudscraper
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


if __name__=='__main__':
	link = input('Enter link: ')
	path = input('Path to save file: ')
	if not path:
		path = '.' # default path
	dl = m3u8downloader() # initialize the downloader
	title, m3u8_url = dl.parse_url(link)
	dl.download_segment(m3u8_url, path, _ishtz=False) # download the segments
	dl.convert('title' + '.mp4', path, keep_cache=False) #concatenate the segments and convert to mp4 by ffmpeg