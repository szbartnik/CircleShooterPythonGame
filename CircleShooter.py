import math
import random
import pygame
import os.path
from abc import ABCMeta, abstractmethod

class Vector2D:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	
	def __iadd__(self, vector):
		self.x += vector.x
		self.y += vector.y
		return self
	
	def __isub__(self, vector):
		self.x -= vector.x
		self.y -= vector.y
		return self
	
	def copy(self, vector):
		self.x = vector.x
		self.y = vector.y

class Colors: 
	BLACK = (0,     0,   0)
	GREEN = (0,   204,   0)
	RED   = (204, 204, 204)
	WHITE = (255, 255, 255)

class Bubble2D(Renderable_object):
	def __init__(self, game, radius):
		Renderable_object.__init__(self, game, Vector2D(0, 0))
		self.radius = radius
		self.speed = Vector2D(0, 0)
	
	def update(self, delta_t):
		self.pos.x += self.speed.x * delta_t
		self.pos.y += self.speed.y * delta_t
		
	def wrap_around():
		pos = self.pos
		if pos.x < 0: pos.x = 1
		if pos.y < 0: pos.y = 1
		if pos.x > 1: pos.x = 0
		if pos.y > 1: pos.y = 0
		
	def is_out(self):
		pos = self.pos
		return (pos.x < 0
			 or pos.y < 0
			 or pos.x > 1
			 or pos.y > 1)
			 
	def is_colliding(self, other):
		x = abs(self.pos.x - other.pos.x)
		y = abs(self.pos.y - other.pos.y)
		dist = math.sqrt(x ** 2 + y ** 2)
		return dist < (self.radius + other.radius)
	
class Renderable_object:
	__metaclass__ = ABCMeta
	
	is_active = True
	
	def __init__(self, game, pos):
		self.game = game
		self.pos = pos
		
	def get_fixed_position(self):
		x = int(round(self.pos.x * self.game.dims.x))
		y = int(round(self.pos.y * self.game.dims.y))
		return x, y
	
	@abstractmethod
	def render(self):
		pass

class Ship(Bubble2D):
	def __init__(self, game):
		Bubble2D.__init__(self, game)
	
	def update(self, delta_t):
		super(Bubble2D, self).update(delta_t)
		self.wrap_around()
	
	def render(self):
		bbox = pygame.draw.circle(
			self.game.screen,
			Colors.SILVER,
			self.get_fixed_position(),
			int(round(self.radius * self.game.dims.y)
	
class Bullet(Bubble2D):
	def __init__(self, game):
		Bubble2D.__init__(self, game)

	def update(self, delta_t):
		super(Bullet, self).update(delta_t)
		if(self.is_out()):
			self.is_active = False
		
	def render(self):
		pygame.draw.circle(
			self.game.screen,
			Colors.RED,
			self.get_fixed_position(),
			int(round(self.radius * self.game.dims.y)))

class Power_up(Bubble2D):
	def __init__(self, game):
		Bubble2D.__init__(self, game)
	
	def update(self, delta_t):
		super(Power_up, self).update(delta_t)
	
	def render(self):
		
	
class Enemy(Bubble2D):
	def __init__(self, game):
		Bubble2D.__init__(self, game)
	
	def update(self, delta_t):
		super(Enemy, self).update(delta_t)
		self.wrap_around()

	def render(self):
		
	
class Game:
	dims = Vector2D(640, 480)

	def __init__(self):
		self.screen = pygame.display.set_mode(self.dims.x, self.dims.y)
		