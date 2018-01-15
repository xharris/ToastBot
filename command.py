class Command():
	prefix = '=',
	def __init__(self, message):
		self.message = message
		self.is_valid = message.content.startswith(Command.prefix)
		self.args = []

		if self.is_valid:
			self.args = message.content[len(Command.prefix):].split(' ')

	# get an arg
	def get(self, i):
		if i >= 0 and i < len(self.args):
			return self.args[i]
		return ''

	# map commands to functions and execute correct branch
	async def map(self, tree):
		def runCommand(branch, arg_i=0):
			cmd_part = self.get(arg_i)

			# end of tree, bad command
			if not cmd_part in branch:
				return lambda args: print('bad command: '+' '.join(self.args))
			# move farther down the tree
			elif isinstance(branch[cmd_part], dict):
				return runCommand(branch[cmd_part], arg_i+1)
			# end of tree, good command
			else:
				return branch[cmd_part]

		func = runCommand(tree)
		try:
			await func(self.message, self.args)
		except:
			pass