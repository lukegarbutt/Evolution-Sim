#There is a youtube video showing how this works on my channel right here 
#https://www.youtube.com/watch?v=KMeT2k1ytYs&lc=z13ne1urvyvhzbqf523jzl0ovtupxbzlw


import pygame
import time
import random
import math
import numpy
from pygame import gfxdraw


def main():
	pygame.init()
	game_width = 800
	game_height = 600
	white = (255,255,255)
	black = (0,0,0)
	red = (255,0,0)
	green = (0,255,0)
	blue = (0,0,255)
	fps = 60
	size = 5
	mutation_rate = 0.2
	steering_weights = 0.05
	perception_radius_mutation_range = 30
	reproduction_rate = 0.0005
	initial_perception_radius = 100
	boundary_size = 10
	max_vel = 10
	initial_max_force = 0.02
	health = 100
	max_poison = 50
	nutrition = [20, -80]
	bots = []
	food = []
	poison = []
	oldest_ever = 0
	oldest_ever_dna = []
	gameDisplay = pygame.display.set_mode((game_width, game_height))
	clock = pygame.time.Clock()

	def lerp():
		percent_health = bot.health/health
		lerped_colour = (max(min((1-percent_health)*255,255),0), max(min(percent_health*255,255),0), 0)
		return(lerped_colour)

	def magnitude_calc(vector):
		x = 0
		for i in vector:
			x += i**2
		magnitude = x**0.5
		return(magnitude)

	def normalise(vector):
		magnitude = magnitude_calc(vector)
		if magnitude != 0:
			vector = vector/magnitude
		return(vector)

	class create_bot(): #How to input dna????
		def __init__(self, x, y, dna=False):
			self.position = numpy.array([x,y], dtype='float64')
			self.velocity = numpy.array([random.uniform(-max_vel,max_vel),random.uniform(-max_vel,max_vel)], dtype='float64')
			self.acceleration = numpy.array([0, 0], dtype='float64')
			self.colour = green
			self.health = health
			self.max_vel = 2
			self.max_force = 0.5
			self.size = 5
			self.age = 1

			if dna != False:
				self.dna = []
				for i in range(len(dna)):
					if random.random() < mutation_rate:
						if i < 2:
							self.dna.append(dna[i] + random.uniform(-steering_weights, steering_weights))
						else:
							self.dna.append(dna[i] + random.uniform(-perception_radius_mutation_range, perception_radius_mutation_range))

					else:
						self.dna.append(dna[i])
			else:
				self.dna = [random.uniform(-initial_max_force, initial_max_force), random.uniform(-initial_max_force, initial_max_force), random.uniform(0, initial_perception_radius), random.uniform(0, initial_perception_radius)]
			print(self.dna)

		def update(self):
			self.velocity += self.acceleration

			self.velocity = normalise(self.velocity)*self.max_vel

			self.position += self.velocity
			self.acceleration *= 0
			self.health -= 0.2
			self.colour = lerp()
			self.health = min(health, self.health)
			if self.age % 1000 == 0:
				print(self.age, self.dna)
			self.age += 1

		def reproduce(self):
			if random.random() < reproduction_rate:
				bots.append(create_bot(self.position[0], self.position[1], self.dna))


		def dead(self):
			if self.health > 0:
				return(False)
			else:
				if self.position[0] < game_width - boundary_size and self.position[0] > boundary_size and self.position[1] < game_height - boundary_size and self.position[1] > boundary_size:
					food.append(self.position)
				return(True)

		def apply_force(self, force):
			self.acceleration += force
			
		def seek(self, target):
			desired_vel = numpy.add(target, -self.position)
			desired_vel = normalise(desired_vel)*self.max_vel
			steering_force = numpy.add(desired_vel, -self.velocity)
			steering_force = normalise(steering_force)*self.max_force
			return(steering_force)
			#self.apply_force(steering_force)

		def eat(self, list_of_stuff, index):
			closest = None
			closest_distance = max(game_width, game_height)
			bot_x = self.position[0]
			bot_y = self.position[1]
			item_number = len(list_of_stuff)-1
			for i in list_of_stuff[::-1]:
				item_x = i[0]
				item_y = i[1]
				distance = math.hypot(bot_x-item_x, bot_y-item_y)
				if distance < 5:
					list_of_stuff.pop(item_number)
					self.health += nutrition[index]
				if distance < closest_distance:
					closest_distance = distance
					closest = i
				item_number -=1
			if closest_distance < self.dna[2 + index]:
				seek = self.seek(closest) # index)
				seek *= self.dna[index]
				seek = normalise(seek)*self.max_force
				self.apply_force(seek)


		def boundaries(self):
			desired = None
			x_pos = self.position[0]
			y_pos = self.position[1]
			if x_pos < boundary_size:
				desired = numpy.array([self.max_vel, self.velocity[1]])
				steer = desired-self.velocity
				steer = normalise(steer)*self.max_force
				self.apply_force(steer)
			elif x_pos > game_width - boundary_size:
				desired = numpy.array([-self.max_vel, self.velocity[1]])
				steer = desired-self.velocity
				steer = normalise(steer)*self.max_force
				self.apply_force(steer)
			if y_pos < boundary_size:
				desired = numpy.array([self.velocity[0], self.max_vel])
				steer = desired-self.velocity
				steer = normalise(steer)*self.max_force
				self.apply_force(steer)
			elif y_pos > game_height - boundary_size:
				desired = numpy.array([self.velocity[0], -self.max_vel])
				steer = desired-self.velocity
				steer = normalise(steer)*self.max_force
				self.apply_force(steer)
			'''if desired != None:
				steer = desired-self.velocity
				steer = normalise(steer)*self.max_force
				self.apply_force(steer)'''


		def draw_bot(self):
			pygame.gfxdraw.aacircle(gameDisplay, int(self.position[0]), int(self.position[1]), 10, self.colour)
			pygame.gfxdraw.filled_circle(gameDisplay, int(self.position[0]), int(self.position[1]), 10, self.colour)
			pygame.draw.circle(gameDisplay, green, (int(self.position[0]), int(self.position[1])), abs(int(self.dna[2])), abs(int(min(2, self.dna[2]))))
			pygame.draw.circle(gameDisplay, red, (int(self.position[0]), int(self.position[1])), abs(int(self.dna[3])), abs(int(min(2, self.dna[3]))))
			pygame.draw.line(gameDisplay, green, (int(self.position[0]), int(self.position[1])), (int(self.position[0] + (self.velocity[0]*self.dna[0]*25)), int(self.position[1] + (self.velocity[1]*self.dna[0]*25))), 3)
			pygame.draw.line(gameDisplay, red, (int(self.position[0]), int(self.position[1])), (int(self.position[0] + (self.velocity[0]*self.dna[1]*25)), int(self.position[1] + (self.velocity[1]*self.dna[1]*25))), 2)
			
	for i in range(10):
		bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height)))
	running = True
	while(running):
		gameDisplay.fill(black)
		if len(bots)<5 or random.random() < 0.0001:
			bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height)))
		if random.random()<0.1:
			food.append(numpy.array([random.uniform(boundary_size, game_width-boundary_size), random.uniform(boundary_size, game_height-boundary_size)], dtype='float64'))
		if random.random()<0.01:
			poison.append(numpy.array([random.uniform(boundary_size, game_width-boundary_size), random.uniform(boundary_size, game_height-boundary_size)], dtype='float64'))
		if len(poison)>max_poison:
			poison.pop(0)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			#print(event)
		

		#print(bots[0].position)
		#print((bots[0].position),(bots[0].position+(-size,0)),(bots[0].position+(-size/2,size)))
		for bot in bots[::-1]:
			bot.eat(food, 0)
			bot.eat(poison, 1)
			bot.boundaries()
			#bot.seek(pygame.mouse.get_pos())
			bot.update()
			if bot.age > oldest_ever:
				oldest_ever = bot.age
				oldest_ever_dna = bot.dna
				print(oldest_ever, oldest_ever_dna)
			bot.draw_bot()
			#pygame.draw.polygon(gameDisplay, bot.colour, ((bot.position),tuple(map(operator.add,bot.position,(-size,0))),tuple(map(operator.add,bot.position,(-size/2,size)))))
			if bot.dead():
				bots.remove(bot)
			else:
				bot.reproduce()

		#if random.random()<0.02:
			#bots.append(create_bot(random.uniform(0,game_width),random.uniform(0,game_height)))

		for i in food:
			pygame.draw.circle(gameDisplay, (0,255,0), (int(i[0]), int(i[1])), 3)
		#pygame.draw.circle(gameDisplay, bot.colour, (int(self.position[0]), int(self.position[1])), 10)
		for i in poison:
			pygame.draw.circle(gameDisplay, (255,0,0), (int(i[0]), int(i[1])), 3)
		pygame.display.update()
		clock.tick(fps)

	pygame.quit()
	quit()




main()