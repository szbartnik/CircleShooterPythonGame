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