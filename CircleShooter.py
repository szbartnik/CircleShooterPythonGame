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
		
	def __imul__(self, vector):
		self.x *= vector.x
		self.y *= vector.y
	
	def copy(self, vector):
		self.x = vector.x
		self.y = vector.y
		
	def zero(self):
		self.x = 0
		self.y = 0

class Colors: 
	BLACK = (0,     0,   0)
	GREEN = (0,   204,   0)
	RED   = (204, 204, 204)
	WHITE = (255, 255, 255)
	
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
			font_name, game.dims.y / 10)
		self.msg_font = pygame.font.SysFont(
			font_name, game.dims.y / 20)
		
class Title_screen(Caption_object):
	def __init__(self, game):
		Caption_object.__init__(self, game)
		
	def render(self):
		text = self.hud_font.render("CIRCLE", False, Colors.GREEN)
		self.game.screen.blit(text, text.get_rect(midbottom = (240, 240)))
		text = self.hud_font.render("SHOOTER", False, Colors.GREEN)
		self.screen.blit(text, text.get_rect(midtop = (240, 240)))
		
		text = self.msg_font.render("No Time To Play", False, Colors.GREEN)
		self.screen.blit(text, text.get_rect(midbottom = (240, 120)))
		text = self.msg_font.render("presents", False, Colors.GREEN)
		self.screen.blit(text, text.get_rect(midtop = (240, 120)))
		
		high_score = "High score: " + str(self.game.high_score)
		text = self.msg_font.render(high_score, False, Colors.GREEN)
		self.game.screen.blit(text, text.get_rect(midbottom = (240, 360)))
		max_level = "Max level: " + str(self.game.max_level)
		text = self.msg_font.render(max_level, False, Colors.GREEN)
		self.game.screen.blit(text, text.get_rect(midtop = (240, 360)))
		
		self.game.screen.fill(Colors.GREEN, (500, 424, 140, 24))
	
class Hud(Caption_object):
	def __init__(self, game):
		Caption_object.__init__(self, game)
		
	def render(self):
		text = self.hud_font.render(str(self.game.level), False, Colors.BLACK)
		self.game.screen.blit(text, (500, 48))
		text = self.hud_font.render(str(self.game.lives), False, Colors.BLACK)
		self.game.screen.blit(text, (500, 48 * 3))
		text = self.hud_font.render(str(self.game.score), False, Colors.BLACK)
		self.game.screen.blit(text, (500, 48 * 5))
		
class Game_messages(Caption_object):
	def __init__(self, game):
		Caption_object.__init__(self, game)
		
	def render(self):
		if (self.game.death_timer > 0) and (self.game.lives < 1):
			text = self.hud_font.render("GAME", False, Colors.GREEN)
			self.game.screen.blit(text, text.get_rect(midbottom = (240, 240)))
			text = self.hud_font.render("OVER", False, Colors.GREEN)
			self.game.screen.blit(text, text.get_rect(midtop = (240, 240)))
		elif self.game.is_paused:
			text = self.msg_font.render("Game paused", False, Colors.GREEN)
			self.game.screen.blit(text, text.get_rect(midbottom = (240, 480)))
	
class Background(Caption_object):
	def __init__(self, game):
		Caption_object.__init__(self, game)
		
	def render(self):
		self.game.bglayer.fill(Colors.BLACK)
		self.game.bglayer.fill(Colors.GREEN, (480, 0, 160, 480))
		
		msg = ["Level", "Lives", "Score"]
		for i in range(3):
			text = self.hud_font.render(msg[i], False, Colors.BLACK)
			self.game.bglayer.blit(text, (500, i * 96))
		
		msg = ["[Q]uit", "[P]ause", "[P]lay"]
		for i in range(3):
			text = self.msg_font.render(msg[i], False, Colors.WHITE)
			self.game.bglayer.blit(text, (500, 448 - i * 24))
	
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
		
class Ship(Bubble2D):
	accel = Vector2D(0, 0)

	def __init__(self, game):
		Bubble2D.__init__(self, game, 1.0 / 25)
		self.pos = Vector2D(0.5, 0.5)
		self.shield_timer = 6
	
	def update(self, delta_t):
		super(Bubble2D, self).update(delta_t)
		self.wrap_around()
	
	def render(self):
		bbox = pygame.draw.circle(
			self.game.screen,
			Colors.SILVER,
			self.get_fixed_position(),
			int(round(self.radius * self.game.dims.y)
			
		pygame.draw.circle(
			self.game.screen,
			Colors.BLACK,
			self.get_fixed_position(),
			int(round(self.radius * 0.5 * self.game.dims.y)),
			1)
			
		if self.shield_timer > 0
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
		else
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
		self.game.ship_shield_timer += 6
	
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
		self.game.freeze_timer += 6
		
	def render(self):
		super(Freeze_power_up, self).render()
	
		radius = self.radius * self.game.dims.y
		pos_x = self.pos.x * self.game.dims.x
		pos_y = self.pos.y * self.game.dims.y
		
		bbox = pygame.rect(0, 0, radius * 2, radius * 2)
		bbox.center = (pos_x, pos_y)
		pygame.draw.rect(self.game.screen, Colors.WHITE, bbox, 1)
		bbox.inflate_ip(-radius, -radius)
		pygame.draw.rect(self.game.screen, Colors.WHITE, bbox, 1)
		bbox.inflate_ip(-radius * 0.5, -radius * 0.5)
		pygame.draw.rect(self.game.screen, Colors.WHITE, bbox, 1)
		
class Enemy(Bubble2D):
	def __init__(self, game, kind):
		Bubble2D.__init__(self, game)
		self.kind = kind
		self.color = random.choice([
			"#ffffcc", "#ffccff", 
		    "#ccffff", "#ffdddd", 
		    "#ddffdd", "#ddddff"])
	
	def random_position():
		return (random.random() - 0.5) * 3 + 0.5;
	random_position = staticmethod(random_position)
	
	def random_speed(magnitude):
		return (random.random() * magnitude * 2 - magnitude)
	random_speed = staticmethod(random_speed)
	
	def spawn(kind, game):
		if kind == "big":
			size = 0.1
			speed = 0.1
		elif kind == "medium":
			size = 0.075
			speed = 0.15
		elif kind == "small":
			size = 0.05
			speed = 0.25
			
		new_enemy = Enemy(game, kind)
		new_enemy.pos = Vector2D(random_position(), random_position())
		new_enemy.speed = Vector2D(random_speed(), random_speed())	
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
	level = 0
	lives = 3
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
		is_paused = not is_paused
	
	def shoot_at(self, x, y):
		if self.bullet != None or self.ship == None:
			return

		x -= self.ship.pos.x;
		y -= self.ship.pos.y;

		bullet = Bullet(self)
		bullet.pos.copy(self.ship.pos);
		bullet.speed.x = x * 3
		bullet.speed.y = y * 3
	
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
		
		self.ship.accel.x += x * 0.03;
		self.ship.accel.y += y * 0.03;
	
	def stop_flying(self):
		if self.ship == None:
			return
		
		self.ship.accel.zero()
	
	def update(self, delta_t):
		self.handle_collisions(delta_t)
		
		# Update explosions
		if len(self.explosions) > 0:
			if self.explosions[0].radius > 0.5:
				self.explosions.pop(0)
		for i in self.explosions:
			i.radius += delta_t
		
		# Update powerups
		if len(self.powerups) > 0:
			if self.powerups[0].age > 9:
				self.powerups.pop(0)
		for i in self.powerups:
			i.age += delta_t
		
		# Update shield timer
		if self.ship_shield_timer > 0:
			self.ship_shield_timer -= delta_t
		
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
				self.level = 0 # Game over
			return
		
		# Ship update
		self.ship.speed += self.ship.accel
		self.ship.speed *= Vector2D(0.99)
		self.ship.update(delta_t)
		
	def handle_collisions(self):
		for e in self.enemies:
			if self.bullet != None and e.collides_with(self.bullet):
				self.enemies.remove(e)
				self.bullet.update(delta_t * 5)
				self.spawn_enemies(e)
				self.spawn_explosion(e)
				self.mark_score(e)
				if len(self.enemies) == 0:
					self.finish_timer = 3
				break
			elif self.ship != None:
				if not e.collides_with(self.ship):
					continue
				if self.ship_shield_timer > 0:
					continue
				self.spawn_explosion(self.ship)
				self.ship = None
				--self.lives
				self.death_timer = 3;

		if self.ship == None:
			return
		
		for p in self.powerups:
			if p.collides_with(self.ship):
				self.apply_powerup(p)
				self.powerups.remove(p)
				
	def spawn_enemies(self, parent):
		if parent.kind == "small":
			if random.random() < 0.25:
				self.spawn_powerup(parent)
		else:
			if parent.kind == "big":
				new_type = "medium"
			elif parent.kind == "medium":
				new_type = "small"
				
			enemy = Enemy.spawn(new_type)
			enemy.position.copy(parent.position)
			self.bubbles.append(enemy)
			enemy = Enemy.spawn(new_type)
			enemy.position.copy(parent.position)
			self.bubbles.append(enemy)
	
	def spawn_explosion(self, enemy):
		explosion = Explosion()
		explosion.position.copy(enemy.position)
		self.explosions.append(explosion)
	
	def spawn_powerup(self, enemy):
		powerup = Power_up.random_power_up(self)
		powerup.position.copy(enemy.position)
		self.powerups.append(powerup)
	
	def mark_score(self, enemy):
		if enemy.kind == "small":
			self.score += 5
		elif enemy.kind == "medium":
			self.score += 2
		elif enemy.kind == "big":
			self.score += 1

		if self.score > self.high_score:
	
	def apply_powerup(self, powerup):
		powerup.use()
		self.score += self.level * 10

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
		self.screen.set_clip((0, 0, 480, 480))
		
		# Render all objects
		map(lambda x: x.render(), filter(lambda y: y != None, get_all_objects()))
		
		self.screen.fill(Colors.GREEN, (500, 400, 140, 24))
		
	def get_all_objects(self):
		return ([ship] + [bullet] + enemies + power_ups + explosions)
	
class Controller:
	def __init__(self):
		# PyGame init
		pygame.init()
		self.dims = Vector2D(640, 480)
		self.screen = pygame.display.set_mode((self.dims.x, self.dims.y))
		self.bglayer = pygame.Surface(screen.get_size())
		
		# Refresh clock
		clock = pygame.time.Clock()
		
		# Init caption
		pygame.display.set_caption("Square Shooter Desktop Edition")
		
		# Steering
		pygame.event.set_blocked(pygame.MOUSEMOTION)
		joystick = pygame.joystick.Joystick(0)
		joystick.init()
		axes = joystick.get_numaxes()
		
	def start(self, game)):
		running = True
		while(running):
			delta_t = clock.tick(60)
			
			# Events handling
			ev = pygame.event.pool()
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
			elif ev_type == pygame.MOUSEBUTTONUP:
				if game.level > 0:
					game.stop_flying()
			
			# Update & render
			if game.level > 0 and not game.is_paused:
				game.update(delta_t * 0.001)
			game.render()

###### ENTRY POINT #######		
controller = Controller()
game = Game(controller)
controller.start(game)