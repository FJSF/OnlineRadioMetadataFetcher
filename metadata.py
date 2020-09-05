import re
import struct
import sys
import multiprocessing

import urllib2
import m3u8

class Station:
	def __init__(self, name, url, song):
			self.name = name
			self.url = url
			self.song = song

def get_metadata(url):
	try:
		encoding = 'utf-8'
		request = urllib2.Request(url, headers={'Icy-MetaData': 1, 'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'})  # request metadata
		response = urllib2.urlopen(request)
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

def update_metadata(station, send_end):
	station.song = get_metadata(station.url)
	send_end.send([station.url, station.song])

stations = []
processes = []
pipes = []

for arg in sys.argv:
	playlist = m3u8.load(arg)
	for stream in playlist.segments:
		stations.append(Station(stream.title, stream.uri, None))

for station in stations:
	recv_end, send_end = multiprocessing.Pipe(False)
	process = multiprocessing.Process(target=update_metadata, args=(station,send_end))
	processes.append(process)
	pipes.append(recv_end)
	process.start()

for process in processes:
	process.join()

for pipe in pipes:
	data = pipe.recv()
	for station in stations:
		if station.url == data[0]:
			station.song = data[1]
			break

for station in stations:
	if type(station.song) is unicode and station.song != '':
		print station.name + ': ' + station.song
