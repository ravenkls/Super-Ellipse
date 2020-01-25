import pygame
from pygame import gfxdraw
import math
from math import sin, cos
import sys
import random
from audio import SongAnalysis
import numpy as np


# TODO: make colours fade, so that quick flashing images arent as jarring

SONG = 'assets/music/song.wav'
WIDTH = 1280
HEIGHT = 720
FRAMES_PER_SECOND = 60
ARROW_SPEED = 0.15
OBSTACLE_SPAWN_RATE = 750

CREATE_OBSTACLE_EVENT = pygame.USEREVENT + 1
CHANGE_DIRECTION_EVENT = pygame.USEREVENT + 2
PUMP_EVENT = pygame.USEREVENT + 3


BACKGROUND_COLOURS = (
    (255, 61, 61), # red
    (255, 164, 61), # orange
    (145, 255, 61), # green
    (61, 255, 187), # blue
    (61, 116, 255), # darker blue
    (61, 64, 255), # indigo
    (255, 61, 239) # violet
)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Obstacle(pygame.sprite.Sprite):

    thickness = 25

    def __init__(self, gap_angle, gap_width):
        super().__init__()
        self.pump = 0
        self.size = max(WIDTH, HEIGHT) + 300
        self.center = WIDTH//2, HEIGHT//2
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.gap_angle = gap_angle
        self.gap_width = gap_width
        self.gap_line_length = self.thickness * 6
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)

    def update(self):
        self.size -= 10
        draw_size = int(self.size + self.pump)
        
        if draw_size <= 0:
            return self.kill()
        self.image.fill(BLACK)
        
        gfxdraw.filled_circle(self.image, *self.center, draw_size//2, WHITE)
        if draw_size//2 > self.thickness:
            gfxdraw.filled_circle(self.image, *self.center, draw_size//2-self.thickness, BLACK)
        

        self.gap_line_start = (self.center[0] + int((draw_size//2 - self.gap_line_length//2) * cos(self.gap_angle)),
                               self.center[1] + int((draw_size//2 - self.gap_line_length//2) * sin(self.gap_angle)))
        self.gap_line_point = (self.gap_line_start[0] + int(self.gap_line_length * cos(self.gap_angle)),
                               self.gap_line_start[1] + int(self.gap_line_length * sin(self.gap_angle)))

        pygame.draw.line(self.image, BLACK, self.gap_line_start, self.gap_line_point, 100)

        self.mask = pygame.mask.from_surface(self.image, 50)

        self.rect.center = self.center


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image_file = pygame.image.load('assets/images/arrow.png')
        self.arrow = pygame.transform.scale(self.image_file, (13, 8))
        self.mask = pygame.mask.from_surface(self.arrow)
        self.pump = 0
        self.image = self.arrow
        self.rect = self.image.get_rect()
        self.center_point = (0, 0)
        self.angle = 0
        self.r = 100

    @property
    def angle(self):
        return self.theta
    
    @angle.setter
    def angle(self, value):
        degrees = 180 + value * 180 / math.pi
        self.image = pygame.transform.rotate(self.arrow, degrees)
        self.theta = value

    def set_center_point(self, x, y):
        self.center_point = x, y

    def update(self):
        self.rect.centerx = int(self.center_point[0] + (self.r + self.pump) * sin(self.theta))
        self.rect.centery = int(self.center_point[1] + (self.r + self.pump) * cos(self.theta))
        

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.mixer.music.load(SONG)
pygame.mixer.music.play(-1)

song = SongAnalysis(SONG)

pygame.time.set_timer(CREATE_OBSTACLE_EVENT, OBSTACLE_SPAWN_RATE)
pygame.time.set_timer(CHANGE_DIRECTION_EVENT, 1000)

player = Player()
player.set_center_point(WIDTH//2, HEIGHT//2)

entities = pygame.sprite.Group()
entities.add(player)

obstacles = pygame.sprite.Group()

left = 0
right = 0

screen_rotation_speed = 0.01

pump = 0
last_pump = 0
last_colour_change = 0

current_background = np.array([random.choice(BACKGROUND_COLOURS)])

while True:

    clock.tick(FRAMES_PER_SECOND)
    obstacles.update()
    entities.update()

    last_pump = pump

    if pump > 0:
        pump //= 1.1
        pump = int(pump)
    
    music_pos = pygame.mixer.music.get_pos()
    pump = int(max(song.calculate_amps(music_pos)[:10]) * 100)
    
    if pump >= 45 and last_pump <= 45 and last_colour_change > 20:
        new_background = current_background[0]
        while tuple(new_background) == tuple(current_background[0]):
            new_background = random.choice(BACKGROUND_COLOURS)
        current_background = np.linspace(current_background[0], new_background, int(FRAMES_PER_SECOND * 0.1))
        last_colour_change = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                left = ARROW_SPEED
            elif event.key == pygame.K_RIGHT:
                right = ARROW_SPEED
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                left = 0
            elif event.key == pygame.K_RIGHT:
                right = 0
        elif event.type == CREATE_OBSTACLE_EVENT:
            angle = random.random() * 2 * math.pi
            width = random.randrange(20) + 100
            obstacle = Obstacle(angle, width)
            obstacles.add(obstacle)
        elif event.type == CHANGE_DIRECTION_EVENT:
            if random.randrange(10) == 0:
                speed = random.randint(1, 3) / 100
                direction = random.choice((-1, 1))
                screen_rotation_speed = speed * direction

    for n, obstacle in enumerate(obstacles):
        if n < 1:
            if pygame.sprite.collide_mask(obstacle, player):
                sys.exit()
        obstacle.gap_angle += screen_rotation_speed
        obstacle.pump = pump

    player.angle += left - right - screen_rotation_speed
    player.pump = pump//5

    screen.fill(current_background[0])
    if len(current_background) > 1:
        current_background = np.delete(current_background, 0, axis=0)
    last_colour_change += 1

    obstacles.draw(screen)
    entities.draw(screen)
    
    gfxdraw.aacircle(screen, WIDTH//2, HEIGHT//2, 60 + pump//5, WHITE)
    gfxdraw.filled_circle(screen, WIDTH//2, HEIGHT//2, 60 + pump//5, WHITE)

    pygame.display.flip()