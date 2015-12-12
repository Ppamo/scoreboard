import config, datetime
from threading import Timer
import RPi.GPIO as GPIO

class button_handler(object):

	def __init__(self, config):
		self.config = config
		self.a_pin = 18
		self.b_pin = 23
		self.c_pin = 24
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.a_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.b_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.c_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(self.a_pin, GPIO.BOTH, callback=self.button_callback)
		GPIO.add_event_detect(self.b_pin, GPIO.BOTH, callback=self.button_callback)
		GPIO.add_event_detect(self.c_pin, GPIO.BOTH, callback=self.button_callback)
		self.a_click_callbacks = []
		self.a_hold_callbacks = []
		self.b_click_callbacks = []
		self.b_hold_callbacks = []
		self.c_click_callbacks = []
		self.c_hold_callbacks = []
		self.click_callbacks_by_channel = { self.a_pin: self.a_click_callbacks, self.b_pin: self.b_click_callbacks, self.c_pin: self.c_click_callbacks }
		self.hold_callbacks_by_channel = { self.a_pin: self.a_hold_callbacks, self.b_pin: self.b_hold_callbacks, self.c_pin: self.c_hold_callbacks }
		self.click_event_timer = {}
		self.event_delta = datetime.timedelta(milliseconds = 500)
		self.event_hold_delta = datetime.timedelta(milliseconds = 1000)
		dummy_event = {'time': datetime.datetime.now(), 'status': -1}
		self.last_pressed_event = {18: dummy_event, 23: dummy_event, 24: dummy_event}
		self.last_triggered_event = {18: dummy_event, 23: dummy_event, 24: dummy_event}

	def execute_callbacks(self, callbacks):
		for callback in callbacks:
			if callback is not None:
				callback()

	def button_callback(self, channel):
		print "events: button_callback - channel:{}".format(channel)

		# read the channel state
		channel_state = GPIO.input(channel)
		old_state = self.last_pressed_event[channel]['status']

		# do nothing if the event state is the same than the old one
		if (channel_state == old_state):
			return None

		# calculate the time of last event triggered and button push
		now = datetime.datetime.now()
		delta = now - self.last_triggered_event[channel]['time']
		hold_delta = now - self.last_pressed_event[channel]['time']

		self.last_pressed_event.update({channel: { 'time': now, 'status': channel_state }})

		# this value represents the state pressed of the buttons, so I can calcuate if is hold for a while
		press_state = 0 if (channel == 24) else 1

		# do nothing while the button is pressed
		if (channel_state == press_state):
			return None

		# trigger the event
		if delta > self.event_delta:
			if hold_delta > self.event_hold_delta:
				self.last_triggered_event.update({channel: { 'time': now, 'status': 1}})
				self.execute_callbacks(self.hold_callbacks_by_channel[channel])
				print "events: triggered hold event"
			else:
				if channel in self.click_event_timer:
					print "events: cancel click event!"
					self.click_event_timer[channel].cancel()
					del self.click_event_timer[channel]
					self.last_triggered_event.update({channel: { 'time': now, 'status': 2}})
					self.execute_callbacks(self.hold_callbacks_by_channel[channel])
					print "events: triggered double click event at ".format(datetime.datetime.now())
				else:
					print "events: enqueued click event at {}".format(datetime.datetime.now())
					self.click_event_timer.update({channel: Timer(0.4, self.click_trigger, [channel])})
					self.click_event_timer[channel].start()

	def click_trigger(self, channel):
		now = datetime.datetime.now()
		self.last_triggered_event.update({channel: { 'time': now, 'status': 0}})
		self.execute_callbacks(self.click_callbacks_by_channel[channel])
		del self.click_event_timer[channel]
		print "events: triggered click event at {}".format(datetime.datetime.now())

	def add_handler(self, button, handler = None, event = 'click'):
		if button == 'a':
			list = self.a_click_callbacks if event == 'click' else self.a_hold_callbacks
		elif button == 'b':
			list = self.b_click_callbacks if event == 'click' else self.b_hold_callbacks
		elif button == 'c':
			list = self.c_click_callbacks if event == 'click' else self.c_hold_callbacks
		list.append(handler);
		return len(list) - 1
	
	def remove_handler(self, button, index, event = 'click'):
		if button == 'a':
			list = self.a_click_callbacks if event == 'click' else self.a_hold_callbacks
		elif button == 'b':
			list = self.b_click_callbacks if event == 'click' else self.b_hold_callbacks
		elif button == 'c':
			list = self.c_click_callbacks if event == 'click' else self.c_hold_callbacks
		list[index] = None

	def terminate(self):
		print "events: terminating buttons"
		GPIO.cleanup()


