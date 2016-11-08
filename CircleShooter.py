from __future__ import division
import math
import random
import pygame
import os.path
from abc import ABCMeta, abstractmethod

class ScrCfg:
	width = 800
	height = 600
	h_height = height/2
	q_height = height/4
	f_height = height/5
	t_height = height/10
	bar_width = width - height
	bar_margin = 20
	
class GameCfg:
	freeze_timer = 6
	finish_timer = 3
	death_timer = 3
	
	initial_lives = 3
	bullet_speed_multiplier = 3
	ship_accel_multiplier = 0.03
	ship_resistance = 0.99
	max_explosion_size = 0.5
	power_up_age = 9
	chance_powerup_occurs = 0.25
	
	big_enemy_size = 0.1
	big_enemy_speed = 0.1
	big_enemy_score = 1
	medium_enemy_size = 0.075
	medium_enemy_speed = 0.15
	medium_enemy_score = 2
	small_enemy_size = 0.05
	small_enemy_speed = 0.25
	small_enemy_score = 5
	
	level_score_multiplier = 10

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
		
	def __imul__(self, vector):
		self.x *= vector.x
		self.y *= vector.y
		return self
	
	def copy(self, vector):
		self.x = vector.x
		self.y = vector.y
		
	def zero(self):
		self.x = 0
		self.y = 0
		
class Colors: 
	BLACK  = (  0,   0,   0)
	GREEN  = (  0, 204,   0)
	BLUE   = ( 20, 100, 190)
	RED    = (255,   0,   0)
	SILVER = (204, 204, 204)
	WHITE  = (255, 255, 255)
	
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

class Caption_object(Renderable_object):
	def __init__(self, game):
		Renderable_object.__init__(self, game, Vector2D(0, 0))
		font_name = pygame.font.get_default_font()
		self.hud_font = pygame.font.SysFont(
			font_name, game.dims.y // 10)
		self.msg_font = pygame.font.SysFont(
			font_name, game.dims.y // 20)
		
class Title_screen(Caption_object):
	def __init__(self, game):
		Caption_object.__init__(self, game)
		
	def render(self):
		text = self.hud_font.render("CIRCLE", False, Colors.BLUE)
		self.game.screen.blit(text, text.get_rect(midbottom = (ScrCfg.h_height, ScrCfg.h_height)))
		text = self.hud_font.render("SHOOTER", False, Colors.BLUE)
		self.game.screen.blit(text, text.get_rect(midtop = (ScrCfg.h_height, ScrCfg.h_height)))
		
		text = self.msg_font.render("Szymon Bartnik (OS2) 2016", False, Colors.BLUE)
		self.game.screen.blit(text, text.get_rect(midbottom = (ScrCfg.h_height, ScrCfg.q_height)))
		
		high_score = "High score: " + str(self.game.high_score)
		text = self.msg_font.render(high_score, False, Colors.BLUE)
		self.game.screen.blit(text, text.get_rect(midbottom = (ScrCfg.h_height, ScrCfg.q_height * 3)))
		max_level = "Max level: " + str(self.game.max_level)
		text = self.msg_font.render(max_level, False, Colors.BLUE)
		self.game.screen.blit(text, text.get_rect(midtop = (ScrCfg.h_height, ScrCfg.q_height * 3)))
	
class Hud(Caption_object):
	def __init__(self, game):
		Caption_object.__init__(self, game)
		
	def render(self):
		text = self.hud_font.render(str(self.game.level), False, Colors.BLACK)
		self.game.screen.blit(text, (ScrCfg.height + ScrCfg.bar_margin, ScrCfg.bar_margin + ScrCfg.t_height))
		text = self.hud_font.render(str(self.game.lives), False, Colors.BLACK)
		self.game.screen.blit(text, (ScrCfg.height + ScrCfg.bar_margin, ScrCfg.bar_margin + ScrCfg.t_height * 3))
		text = self.hud_font.render(str(self.game.score), False, Colors.BLACK)
		self.game.screen.blit(text, (ScrCfg.height + ScrCfg.bar_margin, ScrCfg.bar_margin + ScrCfg.h_height))
		
class Game_messages(Caption_object):
	def __init__(self, game):
		Caption_object.__init__(self, game)
		
	def render(self):
		if (self.game.death_timer > 0) and (self.game.lives < 1):
			text = self.hud_font.render("GAME", False, Colors.BLUE)
			self.game.screen.blit(text, text.get_rect(midbottom = (ScrCfg.h_height, ScrCfg.h_height)))
			text = self.hud_font.render("OVER", False, Colors.BLUE)
			self.game.screen.blit(text, text.get_rect(midtop = (ScrCfg.h_height, ScrCfg.h_height)))
		elif self.game.is_paused:
			text = self.msg_font.render("Game paused", False, Colors.BLUE)
			self.game.screen.blit(text, text.get_rect(midbottom = (ScrCfg.width, ScrCfg.height)))
	
class Background(Caption_object):
	def __init__(self, game):
		Caption_object.__init__(self, game)
		
	def render(self):
		self.game.bglayer.fill(Colors.BLACK)
		self.game.bglayer.fill(Colors.BLUE, (ScrCfg.height, 0, ScrCfg.bar_width, ScrCfg.height))
		
		msg = ["Level", "Lives", "Score"]
		for i in range(len(msg)):
			text = self.hud_font.render(msg[i], False, Colors.BLACK)
			self.game.bglayer.blit(text, (ScrCfg.height + ScrCfg.bar_margin, ScrCfg.bar_margin + i * ScrCfg.t_height * 2))
		
		msg = ["[P]lay/[P]ause", "[Q]uit"]
		for i in range(len(msg)):
			text = self.msg_font.render(msg[i], False, Colors.WHITE)
			self.game.bglayer.blit(text, (ScrCfg.height + ScrCfg.bar_margin, ScrCfg.height - (len(msg)-i) * ScrCfg.t_height / 2))
	
class Bubble2D(Renderable_object):
	def __init__(self, game, radius):
		Renderable_object.__init__(self, game, Vector2D(0, 0))
		self.radius = radius
		self.speed = Vector2D(0, 0)
	
	def update(self, delta_t):
		self.pos.x += self.speed.x * delta_t
		self.pos.y += self.speed.y * delta_t
		
	def wrap_around(self):
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
	accel = Vector2D(0, 0)

	def __init__(self, game):
		Bubble2D.__init__(self, game, 1 / 25)
		self.pos = Vector2D(0.5, 0.5)
		self.shield_timer = 6
	
	def update(self, delta_t):
		super(Ship, self).update(delta_t)
		self.wrap_around()
	
	def render(self):
		bbox = pygame.draw.circle(
			self.game.screen,
			Colors.SILVER,
			self.get_fixed_position(),
			int(round(self.radius * self.game.dims.y)))
			
		pygame.draw.circle(
			self.game.screen,
			Colors.BLACK,
			self.get_fixed_position(),
			int(round(self.radius * 0.5 * self.game.dims.y)),
			1)
			
		if self.shield_timer > 0:
			pygame.draw.rect(self.game.screen, Colors.SILVER, bbox, 1)
			
class Bullet(Bubble2D):
	def __init__(self, game):
		Bubble2D.__init__(self, game, 0.01)

	def update(self, delta_t):
		super(Bullet, self).update(delta_t)
		if self.is_out():
			self.is_active = False
		
	def render(self):
		pygame.draw.circle(
			self.game.screen,
			Colors.RED,
			self.get_fixed_position(),
			int(round(self.radius * self.game.dims.y)))

class Power_up(Bubble2D):
	age = 0

	def __init__(self, game):
		Bubble2D.__init__(self, game, 0.03)
	
	def random_power_up(game):
		if random.random() > 0.5:
			return Shield_power_up(game)
		else:
			return Freeze_power_up(game)
	random_power_up = staticmethod(random_power_up)
	
	def update(self, delta_t):
		super(Power_up, self).update(delta_t)
	
	def render(self):
		pass
		
class Shield_power_up(Power_up):
	def __init__(self, game):
		Power_up.__init__(self, game)
	
	def use(self):
		self.game.ship.shield_timer += 6
	
	def render(self):
		super(Shield_power_up, self).render()
		bbox = pygame.draw.circle(
			self.game.screen,
			Colors.WHITE,
			self.get_fixed_position(),
			int(round(self.radius * self.game.dims.y)),
			1)
		pygame.draw.rect(self.game.screen, Colors.WHITE, bbox, 1)
		
class Freeze_power_up(Power_up):
	def __init__(self, game):
		Power_up.__init__(self, game)
		
	def use(self):
		self.game.freeze_timer += GameCfg.freeze_timer
		
	def render(self):
		super(Freeze_power_up, self).render()
	
		radius = self.radius * self.game.dims.y
		pos_x = self.pos.x * self.game.dims.x
		pos_y = self.pos.y * self.game.dims.y
		
		bbox = pygame.Rect(0, 0, radius * 2, radius * 2)
		bbox.center = (pos_x, pos_y)
		pygame.draw.rect(self.game.screen, Colors.WHITE, bbox, 1)
		bbox.inflate_ip(-radius, -radius)
		pygame.draw.rect(self.game.screen, Colors.WHITE, bbox, 1)
		bbox.inflate_ip(-radius * 0.5, -radius * 0.5)
		pygame.draw.rect(self.game.screen, Colors.WHITE, bbox, 1)
		
class Enemy(Bubble2D):
	def __init__(self, game, kind, size):
		Bubble2D.__init__(self, game, size)
		self.kind = kind
		self.color = random.choice(map(lambda x: pygame.Color(x), [
			"#ffffcc", "#ffccff", 
		    "#ccffff", "#ffdddd", 
		    "#ddffdd", "#ddddff"]))
	
	def random_position():
		return (random.random() - 0.5) * 3 + 0.5;
	random_position = staticmethod(random_position)
	
	def random_speed(magnitude):
		return (random.random() * magnitude * 2 - magnitude)
	random_speed = staticmethod(random_speed)
	
	def spawn(kind, game):
		if kind == "big":
			size = GameCfg.big_enemy_size
			speed = GameCfg.big_enemy_speed
		elif kind == "medium":
			size = GameCfg.medium_enemy_size
			speed = GameCfg.medium_enemy_speed
		elif kind == "small":
			size = GameCfg.small_enemy_size
			speed = GameCfg.small_enemy_speed
			
		new_enemy = Enemy(game, kind, size)
		new_enemy.pos = Vector2D(Enemy.random_position(), Enemy.random_position())
		new_enemy.speed = Vector2D(Enemy.random_speed(speed), Enemy.random_speed(speed))	
		return new_enemy
	spawn = staticmethod(spawn)
	
	def update(self, delta_t):
		super(Enemy, self).update(delta_t)
		self.wrap_around()

	def render(self):
		pygame.draw.circle(
			self.game.screen,
			self.color,
			self.get_fixed_position(),
			int(round(self.radius * self.game.dims.y)),
			1)
			
class Explosion(Bubble2D):
	def __init__(self, game):
		Bubble2D.__init__(self, game, 0)
	
	def update(self, delta_t):
		super(Explosion, self).update(delta_t)
	
	def render(self):
		pygame.draw.circle(
			self.game.screen,
			Colors.RED,
			self.get_fixed_position(),
			int(round(self.radius * self.game.dims.y)),
			1)
	
class Game:
	# Current statistics
	lives = GameCfg.initial_lives
	level = 0
	score = 0
	
	# Permanent statistics
	high_score = 0
	max_level  = 0
	
	# Time management
	death_timer  = 0
	finish_timer = 0
	freeze_timer = 0
	is_paused = False
	
	# Game objects
	ship   = None
	bullet = None
	enemies    = []
	power_ups  = []
	explosions = []
	
	def __init__(self, controller):
		self.dims    = controller.dims
		self.screen  = controller.screen
		self.bglayer = controller.bglayer
	
		self.hud_obj           = Hud(self)
		self.title_screen_obj  = Title_screen(self)
		self.game_messages_obj = Game_messages(self)
		self.background_obj    = Background(self)
		
		self.background_obj.render()
	
	def init_game(self, level):
		self.level = level
		
		# Update statistics
		if level > self.max_level: 
			self.max_level = level
		
		# Remove all objects
		self.ship = None
		self.bullet = None
		del self.enemies[:]
		del self.power_ups[:]
		del self.explosions[:]
		
		# Spawn new objects
		self.ship = Ship(self)
		for i in range(level):
			self.enemies.append(Enemy.spawn("big", self))
	
	def toggle_pause(self):
		self.is_paused = not self.is_paused
	
	def shoot_at(self, x, y):
		if self.bullet != None or self.ship == None:
			return

		x -= self.ship.pos.x;
		y -= self.ship.pos.y;

		bullet = Bullet(self)
		bullet.pos.copy(self.ship.pos);
		bullet.speed.x = x * GameCfg.bullet_speed_multiplier
		bullet.speed.y = y * GameCfg.bullet_speed_multiplier
	
		absx = abs(x)
		absy = abs(y)
		if absx < 0.1 and absy < 0.1:
			bullet.speed.x *= 30
			bullet.speed.y *= 30
			
		self.bullet = bullet
	
	def fly_to(self, x, y):
		if self.ship == None:
			return

		x -= self.ship.pos.x;
		y -= self.ship.pos.y;
		
		self.ship.accel.x += x * GameCfg.ship_accel_multiplier;
		self.ship.accel.y += y * GameCfg.ship_accel_multiplier;
	
	def stop_flying(self):
		if self.ship == None:
			return
		
		self.ship.accel.zero()
	
	def update(self, delta_t):
		self.handle_collisions(delta_t)
		
		self.remove_inactive_objects()
		
		# Update explosions
		if len(self.explosions) > 0:
			if self.explosions[0].radius > GameCfg.max_explosion_size:
				self.explosions.pop(0)
		for i in self.explosions:
			i.radius += delta_t
		
		# Update powerups
		if len(self.power_ups) > 0:
			if self.power_ups[0].age > GameCfg.power_up_age:
				self.power_ups.pop(0)
		for i in self.power_ups:
			i.age += delta_t
		
		# Update freeze timer
		if self.freeze_timer > 0:
			self.freeze_timer -= delta_t
		
		if len(self.enemies) == 0:
			# Update finish timer
			if self.finish_timer > 0:
				self.finish_timer -= delta_t;
			else:
				# Level up
				++self.level
				++self.lives
				self.init_game(self.level)
				return
		# Update enemies
		elif self.freeze_timer <= 0:
			for e in self.enemies:
				e.update(delta_t)
		
		# Bullet update
		if self.bullet != None:
			self.bullet.update(delta_t)
		
		# Ship spawn
		if self.ship == None:
			if self.death_timer > 0:
				self.death_timer -= delta_t
			elif self.lives > 0:
				self.ship = Ship(self)
			else:
				self.level = 0
			return
		
		# Update shield timer
		if self.ship.shield_timer > 0:
			self.ship.shield_timer -= delta_t
		
		# Ship update
		self.ship.speed += self.ship.accel
		self.ship.speed *= Vector2D(GameCfg.ship_resistance, GameCfg.ship_resistance)
		self.ship.update(delta_t)
		
	def handle_collisions(self, delta_t):
		for e in self.enemies:
			if self.bullet != None and e.is_colliding(self.bullet):
				self.enemies.remove(e)
				self.bullet.update(delta_t * 5)
				self.spawn_enemies(e)
				self.spawn_explosion(e)
				self.mark_score(e)
				if len(self.enemies) == 0:
					self.finish_timer = GameCfg.finish_timer
				break
			elif self.ship != None:
				if not e.is_colliding(self.ship):
					continue
				if self.ship.shield_timer > 0:
					continue
				self.spawn_explosion(self.ship)
				self.ship = None
				--self.lives
				self.death_timer = GameCfg.death_timer;

		if self.ship == None:
			return
		
		for p in self.power_ups:
			if p.is_colliding(self.ship):
				self.apply_powerup(p)
				self.power_ups.remove(p)
				
	def spawn_enemies(self, parent):
		if parent.kind == "small":
			if random.random() < GameCfg.chance_powerup_occurs:
				self.spawn_powerup(parent)
		else:
			if parent.kind == "big":
				new_type = "medium"
			elif parent.kind == "medium":
				new_type = "small"
				
			enemy = Enemy.spawn(new_type, self)
			enemy.pos.copy(parent.pos)
			self.enemies.append(enemy)
			enemy = Enemy.spawn(new_type, self)
			enemy.pos.copy(parent.pos)
			self.enemies.append(enemy)
	
	def spawn_explosion(self, enemy):
		explosion = Explosion(self)
		explosion.pos.copy(enemy.pos)
		self.explosions.append(explosion)
	
	def spawn_powerup(self, enemy):
		powerup = Power_up.random_power_up(self)
		powerup.pos.copy(enemy.pos)
		self.power_ups.append(powerup)
	
	def mark_score(self, enemy):
		if enemy.kind == "small":
			self.score += GameCfg.small_enemy_score
		elif enemy.kind == "medium":
			self.score += GameCfg.medium_enemy_score
		elif enemy.kind == "big":
			self.score += GameCfg.big_enemy_score

		if self.score > self.high_score:
			self.high_score = self.score
	
	def apply_powerup(self, powerup):
		powerup.use()
		self.score += self.level * GameCfg.level_score_multiplier

		# Update high score
		if self.score > self.high_score:
			self.high_score = self.score

	def render(self):
		self.screen.blit(self.bglayer, (0, 0))
		
		if self.level == 0:
			self.title_screen_obj.render()
		else:
			self.render_game_objects()
			self.game_messages_obj.render()
			
		self.hud_obj.render()

		pygame.display.flip()
	
	def render_game_objects(self):
		self.screen.set_clip((0, 0, ScrCfg.height, ScrCfg.height))
		
		# Render all objects
		map(lambda x: x.render(), self.get_all_objects())
		
		self.screen.set_clip(None)
		
	def get_all_objects(self):
		return filter(lambda x: x != None, (
			[self.ship] + 
			[self.bullet] + 
			self.enemies + 
			self.power_ups + 
			self.explosions))
			
	def remove_inactive_objects(self):
		if self.bullet and (not self.bullet.is_active):
			self.bullet = None
	
class Controller:
	def __init__(self):
		# PyGame init
		pygame.init()
		self.dims = Vector2D(ScrCfg.width, ScrCfg.height)
		self.screen = pygame.display.set_mode((self.dims.x, self.dims.y))
		self.bglayer = pygame.Surface(self.screen.get_size())
		
		# Refresh clock
		self.clock = pygame.time.Clock()
		
		# Init caption
		pygame.display.set_caption("Square Shooter Desktop Edition")
		
		# Steering
		pygame.event.set_blocked(pygame.MOUSEMOTION)
		
	def start(self, game):
		running = True
		while(running):
			delta_t = self.clock.tick(60)
			
			# Events handling
			ev = pygame.event.poll()
			if ev.type == pygame.QUIT:
				running = False
			elif ev.type == pygame.KEYUP:
				if ev.key == pygame.K_ESCAPE:
					running = False
				elif ev.key == pygame.K_q:
					if game.level == 0:
						running = False
					else:
						game.init_game(0)
				elif ev.key == pygame.K_p:
					if game.level == 0:
						game.init_game(1)
					else:
						game.toggle_pause()
			elif ev.type == pygame.MOUSEBUTTONDOWN:
				if game.level > 0 and not game.is_paused:
					x, y = ev.pos
					game.shoot_at(x / self.dims.y, y / self.dims.y)
					game.fly_to(x / self.dims.y, y / self.dims.y)
			elif ev.type == pygame.MOUSEBUTTONUP:
				if game.level > 0:
					game.stop_flying()
			
			# Update & render
			if game.level > 0 and not game.is_paused:
				game.update(delta_t * 0.001)
			game.render()

###### ENTRY POINT ######	
controller = Controller()
game = Game(controller)
controller.start(game)