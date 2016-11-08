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