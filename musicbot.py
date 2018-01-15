import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform, os, json
from configparser import SafeConfigParser

from command import Command
from song import Song

easily = 0

class MusicBot(discord.Client):
	def __init__(self):
		super().__init__()
		
		# include ffmpeg and etc
		include_path = ';'+os.path.join(os.getcwd(),'include')
		if not include_path in os.environ['PATH']:
			os.environ['PATH'] += include_path

		#discord.opus.load_opus()
		self.commands = {
			'do': {
				'a': self.cmd_doA,
				'my': self.cmd_doMy
			},
			'join': self.cmd_join,
			'bye': self.cmd_disconnect,
			'shutdown': self.cmd_shutdown,
			'np': self.cmd_nowPlaying,
			'play': self.cmd_play
		}

		self.queue = []
		self.np_song = None
		self.song_data = {}
		'''
			{
				'song': {
					'<UUID>': 'songs/luluco.flac'
				},
				'like': {
					'bob': ['<UUID>', '<UUID>']
				},
				'volume': {
					'<UUID>': 50
				}
			}
		'''
		self.loadSongData()

	async def on_ready(self):
		print('Logged in as '+self.user.name+' (ID:'+self.user.id+') | Connected to '+str(len(self.servers))+' servers | Connected to '+str(len(set(self.get_all_members())))+' users')
		print('--------')
		print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
		print('--------')
		print('Use this link to invite {}:'.format(self.user.name))
		print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(self.user.id))
		print('--------')
		print('Created by Toaxt')

	# bot receives a private message or commmand from server chat
	async def on_message(self, message):
		cmd = Command(message)
		if cmd.is_valid:
			await cmd.map(self.commands)

	def run(self, cfg_path):
		parser = SafeConfigParser()
		parser.read(cfg_path)
		token_id = parser.get('config', 'token_id')

		super().run(token_id)

	def loadSongData(self):
		if not os.path.exists('songs'):
			os.makedir(songs)
		
		s_data = ''
		with open("songs/data.json", "a+") as f_data:
			s_data = f_data.read()
		f_data.close()

		if s_data == '':
			s_data = '{}'
		self.song_data = json.loads(s_data)

	def saveSongData(self):
		s_data = json.dumps(self.song_data)
		f_data = open("songs/data.json", "w+")
		f_data.write(s_data)
		f_data.close()

	# checks if self.voice can be referenced safely
	def isJoined(self):
		return self.voice and self.voice.is_connected()

	def isPlaying(self):
		return self.np_song and not self.np_song.isPlaying()

	def q_addSong(self, song_path):
		self.queue.append(song_path)

	async def q_nextSong(self):
		if len(self.queue) > 0:
			self.np_song = Song(self, 'local', self.queue.pop(0), self.q_nextSong)
			await self.np_song.play()

	async def q_start(self):
		if not self.isPlaying():
			await self.q_nextSong()

	async def cmd_doA(self, msg, args):
		await self.send_message(msg.channel, 'Sure I\'ll do a {}'.format(' '.join(args[2:])))

	async def cmd_doMy(self, msg, args):
		await self.send_message(msg.channel, 'No I will not do your {}'.format(' '.join(args[2:])))

	async def cmd_play(self, msg, args):
		if self.isJoined():
			self.q_addSong('songs/my_leg.mp3')
			self.q_addSong('songs/luluco.flac')
			await self.q_start()

	async def cmd_nowPlaying(self, msg, args):
		await self.send_message(msg.channel, 'Fuck u')

	async def cmd_join(self, msg, args):
		# get channel of user summoning the bot
		auth_voice_state = msg.author.voice
		if not auth_voice_state.is_afk:
			# join the channel
			self.voice = await self.join_voice_channel(auth_voice_state.voice_channel)

	async def cmd_disconnect(self, msg, args):
		if self.isJoined():
			await self.voice.disconnect()
		await self.send_message(msg.channel, 'bye')	

	async def cmd_shutdown(self, msg, args):
		await self.close()
		# next part wont run lol
		await self.send_message(msg.channel, 'you can\'t kill me that easily{}!'.format(' ha ha'*easily))
		easily += 1