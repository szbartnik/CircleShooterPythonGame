import math
import random
import pycontroller
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
	
class Renderable_object:
	__metaclass__ = ABCMeta
	
	is_active = True
	
	def __init__(self, controller, pos):
		self.controller = controller
		self.pos = pos
		
	def get_fixed_position(self):
		x = int(round(self.pos.x * self.controller.dims.x))
		y = int(round(self.pos.y * self.controller.dims.y))
		return x, y
	
	@abstractmethod
	def render(self):
		pass

class Caption_object(Renderable_object):
	def __init__(self, controller):
		Renderable_object.__init__(self, controller, Vector2D(0, 0))
		font_name = pycontroller.font.get_default_font()
		self.hud_font = pycontroller.font.SysFont(
			font_name, controller.dims.y / 10)
		self.msg_font = pycontroller.font.SysFont(
			font_name, controller.dims.y / 20)
		
class Title_screen(Caption_object):
	def __init__(self, controller):
		Caption_object.__init__(self, controller)
		
	def render(self):
		text = self.hud_font.render("CIRCLE", False, Colors.GREEN)
		self.controller.screen.blit(text, text.get_rect(midbottom = (240, 240)))
		text = self.hud_font.render("SHOOTER", False, Colors.GREEN)
		self.screen.blit(text, text.get_rect(midtop = (240, 240)))
		
		text = self.msg_font.render("No Time To Play", False, Colors.GREEN)
		self.screen.blit(text, text.get_rect(midbottom = (240, 120)))
		text = self.msg_font.render("presents", False, Colors.GREEN)
		self.screen.blit(text, text.get_rect(midtop = (240, 120)))
		
		high_score = "High score: " + str(self.controller.high_score)
		text = self.msg_font.render(high_score, False, Colors.GREEN)
		self.screen.blit(text, text.get_rect(midbottom = (240, 360)))
		max_level = "Max level: " + str(self.controller.max_level)
		text = self.msg_font.render(max_level, False, Colors.GREEN)
		self.screen.blit(text, text.get_rect(midtop = (240, 360)))
		
class Bubble2D(Renderable_object):
	def __init__(self, controller, radius):
		Renderable_object.__init__(self, controller, Vector2D(0, 0))
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
		
class Ship(Bubble2D):
	def __init__(self, controller):
		Bubble2D.__init__(self, controller)
		self.shield_timer = 0
	
	def update(self, delta_t):
		super(Bubble2D, self).update(delta_t)
		self.wrap_around()
	
	def render(self):
		bbox = pycontroller.draw.circle(
			self.controller.screen,
			Colors.SILVER,
			self.get_fixed_position(),
			int(round(self.radius * self.controller.dims.y)
			
		pycontroller.draw.circle(
			self.controller.screen,
			Colors.BLACK,
			self.get_fixed_position(),
			int(round(self.radius * 0.5 * self.controller.dims.y)),
			1)
			
		if self.shield_timer > 0
			pycontroller.draw.rect(self.controller.screen, Colors.SILVER, bbox, 1)
			
class Bullet(Bubble2D):
	def __init__(self, controller):
		Bubble2D.__init__(self, controller)

	def update(self, delta_t):
		super(Bullet, self).update(delta_t)
		if self.is_out():
			self.is_active = False
		
	def render(self):
		pycontroller.draw.circle(
			self.controller.screen,
			Colors.RED,
			self.get_fixed_position(),
			int(round(self.radius * self.controller.dims.y)))

class Power_up(Bubble2D):
	def __init__(self, controller):
		Bubble2D.__init__(self, controller)
	
	def update(self, delta_t):
		super(Power_up, self).update(delta_t)
	
	def render(self):
		pass
		
class Shield_power_up(Power_up):
	def __init__(self, controller):
		Power_up.__init__(self, controller)
		
	def render(self):
		super(Shield_power_up, self).render()
		bbox = pycontroller.draw.circle(
			self.controller.screen,
			Colors.WHITE,
			self.get_fixed_position(),
			int(round(self.radius * self.controller.dims.y)),
			1)
		pycontroller.draw.rect(self.controller.screen, Colors.WHITE, bbox, 1)
		
class Freeze_power_up(Power_up):
	def __init__(self, controller):
		Power_up.__init__(self, controller)
		
	def render(self):
		super(Freeze_power_up, self).render()
	
		radius = self.radius * self.controller.dims.y
		pos_x = self.pos.x * self.controller.dims.x
		pos_y = self.pos.y * self.controller.dims.y
		
		bbox = pycontroller.rect(0, 0, radius * 2, radius * 2)
		bbox.center = (pos_x, pos_y)
		pycontroller.draw.rect(self.controller.screen, Colors.WHITE, bbox, 1)
		bbox.inflate_ip(-radius, -radius)
		pycontroller.draw.rect(self.controller.screen, Colors.WHITE, bbox, 1)
		bbox.inflate_ip(-radius * 0.5, -radius * 0.5)
		pycontroller.draw.rect(self.controller.screen, Colors.WHITE, bbox, 1)
		
class Enemy(Bubble2D):
	def __init__(self, controller):
		Bubble2D.__init__(self, controller)
		self.color = random.choice([
			"#ffffcc", "#ffccff", 
		    "#ccffff", "#ffdddd", 
		    "#ddffdd", "#ddddff"])
	
	def update(self, delta_t):
		super(Enemy, self).update(delta_t)
		self.wrap_around()

	def render(self):
		pycontroller.draw.circle(
			self.controller.screen,
			self.color,
			self.get_fixed_position(),
			int(round(self.radius * self.controller.dims.y)),
			1)
			
class Explosion(Bubble2D):
	def __init__(self, controller):
		Bubble2D.__init__(self, controller)
	
	def update(self, delta_t):
		super(Explosion, self).update(delta_t)
		
	def render(self):
		pycontroller.draw.circle(
			self.controller.screen,
			Colors.RED,
			self.get_fixed_position(),
			int(round(self.radius * self.controller.dims.y)),
			1)
	
class Game:
	def __init__(self):
		
	
	def render(self):
		
	
class Controller:
	def __init__(self):
		self.dims = Vector2D(640, 480)
		self.screen = pycontroller.display.set_mode((self.dims.x, self.dims.y))
		self.bglayer = pycontroller.Surface(screen.get_size())

	