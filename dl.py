import os, shutil, math, m3u8, cloudscraper
from urllib.parse import urljoin


class m3u8downloader:
	
	@staticmethod
	def get_context(url: str):
		scraper = cloudscraper.create_scraper()
		return scraper.get(url).text
	
	
	def checkdir(self, path: str):
		path_dir = path + '/vcache'
		if not os.path.exists(path): # check download folder exist if not create new folder
			os.mkdir(path)
		if not os.path.exists(path_dir):
			os.mkdir(path_dir)


	def get_segments_list(self, m3u8_url: str, base_url: str = None):
		base_url = m3u8_url[:(m3u8_url.rfind('/')+1)]
		m3u8_obj = m3u8.loads(self.get_context(m3u8_url))
		bandwidth_max=0
		m3u8_link = ''
		if m3u8_obj.is_variant:
			for playlist in m3u8_obj.playlists:
				bandwidth = playlist.stream_info.bandwidth
				if bandwidth > bandwidth_max: # select variant with highest bandwidth ~ highest resolution
					bandwidth_max = bandwidth
					m3u8_link = playlist.uri
			return self.get_segments_list(urljoin(base_url, m3u8_link), base_url) 
		segment_list = m3u8_obj.files
		for i in range(len(segment_list)):
			segment = segment_list[i]
			if not segment.startswith('http'):
				segment_list[i] = urljoin(base_url, segment)
		return segment_list


	def download_segment(self, m3u8_url: str, download_dir: str = '.', _ishtz: bool = False):
		path_dir = download_dir + '/vcache'
		self.checkdir(download_dir)
		print('Getting segments...')
		segment_url_list = self.get_segments_list(m3u8_url)

		scraper = cloudscraper.create_scraper() # instance for download segments

		i = 1
		l = len(segment_url_list)
		for segment_url in segment_url_list:
			file_name = 'segment-%s.ts' % i
			path = '%s/%s' % (path_dir, file_name)
			percent_ =  math.ceil(i/l*100)
			print(f'[process]: {i}/{l} ~ {percent_}%')
			print('[download]:', segment_url)
			print('[target]:', path)
			print()
			with open(path, 'wb') as f:
				segment_context = scraper.get(segment_url).content
				if _ishtz:
					f.write(segment_context[4:]) # skip first 4 bytes to ignore ffmpeg codec check
				else:
					f.write(segment_context)
			i += 1


	def convert(self, video_name: str, path: str = '.', keep_cache: bool = False):
		video_name = '"' + video_name + '"' # wrap video name with quotes to allow name with space
		self.checkdir(path)
		vcache_dir = path + '/vcache'
		os.chdir(vcache_dir)
		f = open('vcache.txt', 'w')
		i=1
		while True:
			filename = "segment-%i.ts" % i
			if os.path.exists(filename) and os.path.isfile(filename):
				f.write("file %s\n" % filename) # write segments list to vcache.txt
				i += 1
			else:
				break
		f.close()

		os.system("ffmpeg -y -f concat -safe 0 -i vcache.txt -c copy video.ts") # combine all segments to video.ts
		os.system("ffmpeg -y -i video.ts -c copy ../" + video_name) # convert ts file to mp4 format
		if keep_cache:
			list_dir = os.listdir('.')
			size = sum(os.path.getsize(f) for f in list_dir if os.path.isfile(f))
			print("vcache folder has %i files with %i MB you may need to remove!" % (len(list_dir), size/(1024*1024)))
		else:
			os.chdir('..')
			shutil.rmtree('vcache') # clean left overs
