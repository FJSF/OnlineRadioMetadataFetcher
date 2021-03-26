import re
import struct
import sys
import multiprocessing

import urllib.request, urllib.error, urllib.parse
import m3u8

class Station:
	def __init__(self, name, url, song):
			self.name = name
			self.url = url
			self.song = song

def get_metadata(url):
	try:
		encoding = 'utf-8'
		request = urllib.request.Request(url, headers={'Icy-MetaData': 1, 'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'})  # request metadata
		response = urllib.request.urlopen(request)
		metaint = int(response.headers['icy-metaint'])
		response.read(metaint)  # skip to metadata
		metadata_length = struct.unpack('B', response.read(1))[0] * 16  # length byte
		metadata = response.read(metadata_length).rstrip(b'\0')
		# extract title from the metadata
		m = re.search(br"StreamTitle='([^']*)';", metadata)
		if m:
			return m.group(1).decode(encoding)
	except:
		return None

stations = []

for arg in sys.argv:
	playlist = m3u8.load(arg)
	for stream in playlist.segments:
		stations.append(Station(stream.title, stream.uri, None))

for station in stations:
	station.song = get_metadata(station.url)
	if station.song is not None:
		print((station.name + ': ' + station.song))
