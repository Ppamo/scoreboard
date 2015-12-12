import sys

class game_controller(object):

	def __init__(self, config):
		self.config = config
		self.player1 = player('white')
		self.player2 = player('black')
		self.last_scored_player = None
		self.victory_callbacks = []
		self.danger_zone_callbacks = []
		self.combo_breaker_callbacks = []
		self.first_blood_callbacks = []

	def reset(self):
		self.player1.reset()
		self.player2.reset()

	def score(self, player_label):
		# identify the players
		player = self.player1 if player_label == 'white' else self.player2
		other_player = self.player2 if player == self.player1 else self.player1
		is_combo_breaker = other_player.combo_counter > 2
		if player is not self.last_scored_player:
			player.combo_breaker()
			other_player.combo_breaker()
		self.last_scored_player = player
		# score
		player.score()
		self.player1.show_score()
		self.player2.show_score()
		# raise game events
		if player.goal_counter == self.config.max_goals:
			self.victory(player)
		elif player.goal_counter == 1 and other_player.goal_counter == 0:
			self.execute_callbacks(self.first_blood_callbacks)
		elif player.goal_counter == self.config.max_goals - 1:
			self.execute_callbacks(self.danger_zone_callbacks)
		elif is_combo_breaker:
			self.execute_callbacks(self.combo_breaker_callbacks)

	def unscore(self, player_label):
		player = self.player1 if player_label == 'white' else self.player2
		player.unscore()

	def add_handler(self, event_name, handler = None):
		callbacks = {	'victory': self.victory_callbacks,
				'danger_zone': self.danger_zone_callbacks,
				'first_blood': self.first_blood_callbacks,
				'combo_breaker': self.combo_breaker_callbacks
			}
		if event_name in callbacks:
			callbacks[event_name].append(handler)
			return len(callbacks[event_name]) - 1
		else:
			raise Exception('non valid event name: {}'.format(event_name))

	def execute_callbacks(self, callbacks):
		winner = self.get_winner()
		loser = self.player1 if not self.player1 == winner else self.player2
		for callback in callbacks:
			if callback is not None:
				callback(winner, loser)

	def victory(self, player):
		print "victory ... player {} wins".format(player.label)
		player.winner = True
		self.execute_callbacks(self.victory_callbacks)

	def get_winner(self):
		return self.player1 if self.player1.goal_counter >= self.player2.goal_counter else self.player2

	def get_scored_player(self):
		return self.last_scored_player
		
	def get_other_player(self, player):
		return self.player1 if player is not self.player1 else self.player2

class player(object):
	 
	def __init__(self, label):
		self.label = label
	 	self.goal_counter = 0
		self.combo_counter = 0
		self.winner = False

	def reset(self):
		print "{}: reset".format(self.label)
		self.goal_counter = 0
		self.combo_counter = 0

	def score(self):
		self.goal_counter += 1
		self.combo_counter += 1

	def unscore(self):
		self.goal_counter -= 1
		self.combo_counter -= 1

	def show_score(self):
		print "{}: score - {}: combos {}".format(self.label, self.goal_counter, self.combo_counter)

	def combo_breaker(self):
		self.combo_counter = 0


