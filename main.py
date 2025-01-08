from pygame import*
from typing import Any
from random import randint
import os

window_w = 400
window_h = 600
window = display.set_mode((window_w, window_h))
display.set_caption('Jumpy')

clock = time.Clock()
FPS = 60
sroll_top = 200
gravity = 1
max_platforms = 10
scroll = 0
bg_scroll = 0
finish = False
score = 0
fade_counter = 0

if os.path.exists('score.txt'):
	with open('score.txt', 'r') as file:
		high_score = int(file.read())
else:
	high_score = 0

white = (255, 255, 255)
black = (0, 0, 0)
panel = (153, 217, 234)

font.init()
font_small = font.SysFont('Lucida Sans', 20)
font_big = font.SysFont('Lucida Sans', 24)

mixer.init()
mixer.music.load("music.mp3")
mixer.music.set_volume(0.2)
mixer.music.play(-1)
death_sound = mixer.Sound("death.mp3")
death_sound.set_volume(0.4)

player_image = image.load("jump.png").convert_alpha()
bg_image = image.load("bg.png").convert_alpha()
platform_image = image.load("wood.png").convert_alpha()

def draw_text(text, font, color, x, y):
	img = font.render(text, True, color)
	window.blit(img, (x, y))

def draw_panel():
	draw.rect(window, panel, (0, 0, window_w, 30))
	draw.line(window, white, (0, 30), (window_w, 30), 2)
	draw_text('SCORE: ' + str(score), font_small, white, 0, 0)

def draw_bg(bg_scroll):
	window.blit(bg_image, (0, 0 + bg_scroll))
	window.blit(bg_image, (0, -600 + bg_scroll))

class Player():
	def __init__(self, x, y):
		self.image = transform.scale(player_image, (45, 70))
		self.width = 25
		self.height = 65
		self.rect = self.image.get_rect()
		self.rect.center = (x + self.width, y + self.height)
		self.vel_y = 0
		self.flip = False

	def update(self):
		scroll = 0
		dx = 0
		dy = 0

		button = key.get_pressed()
		if button[K_a]:
			dx = -10
			self.flip = True
		if button[K_d]:
			dx = 10
			self.flip = False
		
		self.vel_y += gravity
		dy += self.vel_y
		
		if self.rect.left + dx < 0:
			dx = -self.rect.left
		if self.rect.right + dx > window_w:
			dx = window_w - self.rect.right
		
		for platform in platform_group:
			if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				if self.rect.bottom < platform.rect.centery:
					if self.vel_y > 0:
						self.rect.bottom = platform.rect.top
						dy = 0
						self.vel_y = -20

		if self.rect.top <= sroll_top:
			if self.vel_y < 0:
				scroll = -dy

		self.rect.x += dx
		self.rect.y += dy + scroll

		return scroll

	def draw(self):
		window.blit(transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))


class Platform(sprite.Sprite):
	def __init__(self, x, y, width):
		sprite.Sprite.__init__(self)
		self.image = transform.scale(platform_image, (width, 10))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

	def update(self, scroll):
		self.rect.y += scroll

		if self.rect.top > window_h:
			self.kill()

player = Player(window_w // 2, window_h - 150)

platform_group = sprite.Group()

platform = Platform(window_w // 2 - 50, window_h - 50, 100)
platform_group.add(platform)

game = True
while game == True:
	clock.tick(FPS)

	if finish == False:
		scroll = player.update()
		bg_scroll += scroll
		if bg_scroll >= 600:
			bg_scroll = 0
		draw_bg(bg_scroll)

		if len(platform_group) < max_platforms:
			p_w = randint(40, 60)
			p_x = randint(0, window_w - p_w)
			p_y = platform.rect.y - randint(80, 120)
			platform = Platform(p_x, p_y, p_w)
			platform_group.add(platform)
		platform_group.update(scroll)

		if scroll > 0:
			score += scroll

		draw.line(window, white, (0, score - high_score + sroll_top), (window_w, score - high_score + sroll_top), 3)
		draw_text('HIGH SCORE', font_small, white, window_w - 130, score - high_score + sroll_top)

		platform_group.draw(window)
		player.draw()
		draw_panel()

		if player.rect.top > window_h:
			death_sound.play()
			finish = True

	else:

		if fade_counter < window_w:
			fade_counter += 5

			for y in range(0, 6, 2):
				draw.rect(window, black, (0, y * 100, fade_counter, 100))
				draw.rect(window, black, (window_w - fade_counter, (y + 1) * 100, window_w, 100))

		else:
			draw_text('GAME OVER!', font_big, white, 130, 200)
			draw_text('SCORE: ' + str(score), font_big, white, 130, 250)
			draw_text('PRESS SPACE TO PLAY AGAIN', font_big, white, 40, 300)

			if score > high_score:
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))

			button = key.get_pressed()
			if button[K_SPACE]:
				finish = False
				score = 0
				scroll = 0
				fade_counter = 0
				player.rect.center = (window_w // 2, window_h - 150)
				platform_group.empty()
				platform = Platform(window_w // 2 - 50, window_h - 50, 100)
				platform_group.add(platform)

	for i in event.get():
		if i.type == QUIT:
			if score > high_score:
				high_score = score
				with open('score.txt', 'w') as file:
					file.write(str(high_score))
			game = False

	display.update()