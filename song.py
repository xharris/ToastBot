import discord, os, subprocess, asyncio, re, threading, hashlib

class Song():
	def __init__(self, client, in_type, in_path, fn_after):
		self.path = in_path
		self.type = in_type
		self.name = ''
		self.fn_after = fn_after
		self.is_ready = False
		self.hash = Song.getUUID(in_path)

		# check if song is in autoplay list
		if not self.hash in self.client.song_data:
			self.client.song_data[self.hash] = self.path

		if self.type == 'local':
			self.name = os.path.splitext(os.path.basename(self.path))[0].replace('_',' ')

			args=("ffprobe","-show_entries", "format=duration","-i",self.path)
			popen = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
			output, err = popen.communicate()

			regex = r"(\[FORMAT\][^\d]*[ \s]*duration=)(\d*\.\d+?)([^\d]*[ \s]*\[\/FORMAT\])"
			output = output.decode('UTF-8')
			result = re.match(regex, output)

			if result:
				self.duration = float(result.group(2))
				self.is_ready = True

		self.client = client

	def getUUID(path):
		return str(hashlib.md5(path))

	async def play(self):
		print('playing {} ({}s)'.format(self.name, self.duration))

		# display song playing as game status
		await self.client.change_presence(game=discord.Game(name=self.name))

		player = self.client.voice.create_ffmpeg_player(self.path)
		player.start()

		await asyncio.sleep(self.duration)
		if self.fn_after:
			await self.fn_after()

	def getUUID(self):
		return self.uuid

	def isPlaying(self):
		return self.player.is_playing() or not self.player.is_done()