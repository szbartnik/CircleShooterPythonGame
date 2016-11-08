from __future__ import division
import math
import random
import pygame
from abc import ABCMeta, abstractmethod

execfile('Helpers.py')
execfile('GameCfg.py')
execfile('ScrCfg.py')
execfile('GameObjects.py')

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
		pygame.display.set_caption("Circle Shooter - Szymon Bartnik")
		
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