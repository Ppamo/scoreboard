import pygame, termios, fcntl, sys, os, random, signal
from lib import config, audio_handler, button_handler, game_controller
from espeak import espeak
from threading import Timer

def signal_handler(signal, frame):
	print "signal handler"
	controller.looping = False

class scoreboard():
	def __init__(self):
		print "constructor"
		self.config = config.config()
		self.ac = audio_handler.audio_handler(self.config)
		self.bc = button_handler.button_handler(self.config)
		self.gc = game_controller.game_controller(self.config)
		self.looping = True
		self.keyboard_handlers = {	'q': self.quit,
						'a': self.button_a_onclick,
						'b': self.button_b_onclick,
						'c': self.button_c_onclick  }
		self.combos = {	2: 'dominating',
				3: 'triple',
				4: 'super',
				5: 'hyper',
				6: 'brutal',
				7: 'master',
				8: 'awesome',
				9: 'blaster',
				10: 'monster' }
		self.bc.add_handler('a', self.button_a_onclick, 'click')
		self.bc.add_handler('a', self.button_a_onhold, 'hold')
		self.bc.add_handler('b', self.button_b_onclick, 'click')
		self.bc.add_handler('b', self.button_b_onhold, 'hold')
		self.bc.add_handler('c', self.button_c_onclick, 'click')
		self.gc.add_handler('victory', self.on_game_victory)
		self.gc.add_handler('danger_zone', self.on_danger_zone)
		self.gc.add_handler('first_blood', self.on_first_blood)
		self.gc.add_handler('combo_breaker', self.on_combo_breaker)
		self.score_player = None

	def terminate(self):
		self.ac.terminate()
		self.bc.terminate()

	def quit(self):
		print "quiting"
		self.looping = False

	def button_a_onclick(self):
		self.on_score('white')

	def button_b_onclick(self):
		self.on_score('black')

	def button_c_onclick(self):
		print 'start game'
		self.gc.reset()
		self.ac.stop()
		self.ac.play("crowd")
		if self.score_player is not None:
			self.score_player.cancel()
		self.gc.reset()

	def button_a_onhold(self):
		self.on_unscore('white')

	def button_b_onhold(self):
		self.on_unscore('black')

	def on_score(self, label):
		print 'goal player {}'.format(label)
		self.ac.play("ding")
		self.play_score()
		self.gc.score(label)
		score1 = self.gc.player1.goal_counter
		score2 = self.gc.player2.goal_counter
		combo1 = self.gc.player1.combo_counter
		combo2 = self.gc.player2.combo_counter
		if (combo1 < 2 and combo2 < 2) and (score1 + score2 > 1):
			self.play_tano()
		else:
			self.play_combo()

	def on_unscore(self, label):
		print 'goal player {}'.format(label)
		self.ac.play("ding")
		self.play_score()
		self.gc.unscore(label)

	def on_game_victory(self, winner, loser):
		self.ac.play("victory")
		self.ac.play("winner", 2.0)
		self.ac.play("crowd")
		if self.score_player is not None:
			self.score_player.cancel()
		if loser.goal_counter < 5:
			self.play_random_humilliation()
		print "on victory, player {} wins".format(winner.label)

	def on_danger_zone(self, winner, loser):
		self.ac.play("danger")
		self.ac.play("finishHim", delay = 3.5)

	def on_first_blood(self, player, other):
		self.ac.play("firstBlood", 0.2)

	def on_combo_breaker(self, player, other):
		self.ac.play("comboBreaker", 0.2)

	def play_random_humilliation(self):
		options = {	0: 'humiliation',
				1:'youllNeverWin',
				2:'thatWasPathetic',
				3:'supremeVictory',
				4:'tano'	 }
		option = random.randrange(0,4)
		print 'humiliation: {}'.format(option)
		self.ac.play(options[option], delay = 5.0)

	def play_score(self):
		if self.score_player is not None:
			self.score_player.cancel()
		self.score_player = Timer(2.5, self.play_score_delayed)
		self.score_player.start()

	def play_score_delayed(self):
		score1 = self.gc.player1.goal_counter
		score2 = self.gc.player2.goal_counter
		if score1 != score2:
			self.synth('{} a {}!'.format(score1, score2))
		else:
			self.synth('empate, a {}!'.format(score1))

	def synth(self, message):
		os.system('espeak -ves+m5 "{}" --stdout -a 500 -s 140 -p 80 | aplay'.format(message))

	def play_combo(self):
		player = self.gc.get_scored_player()
		other = self.gc.get_other_player(player)
		if not player.winner and player.combo_counter in self.combos:
			combo = self.combos[player.combo_counter]
			if player.combo_counter == 3 and other.goal_counter == 0:
				combo = 'wickedSick'
			self.ac.play(combo, 0.6)

	def play_tano(self):
		options = {	1:'tano01',
				2:'tano02',
				3:'tano03',
				4:'tano04',
				5:'tano05',
				6:'tano06',
				7:'tano07',
				8:'tano08',
				9:'tano09',
				10:'tano10'	 }
		option = random.randrange(1,9)
		print 'humiliation: {}'.format(option)
		self.ac.play(options[option])
		

	def run(self):
		print "running"
		try:
			self.button_c_onclick()
			while self.looping:
				try:
					c = sys.stdin.read(1)
					if c in self.keyboard_handlers:
						self.keyboard_handlers[c]()
				except IOError: pass
		finally:
			self.terminate()


signal.signal(signal.SIGTERM, signal_handler)
controller = scoreboard()
controller.run()

