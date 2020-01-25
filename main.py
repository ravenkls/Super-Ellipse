import pygame
from pygame import gfxdraw, freetype
import math
from math import sin, cos
import sys
import random
from audio import SongAnalysis
import numpy as np


# TODO: make colours fade, so that quick flashing images arent as jarring

SONG = 'assets/music/stormz2.wav'
WIDTH = 1000
HEIGHT = 700
FRAMES_PER_SECOND = 60
ARROW_SPEED = 0.1
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

    def __init__(self, gap_angles, gap_widths):
        super().__init__()
        self.pump = 0
        self.size = max(WIDTH, HEIGHT) + 300
        self.center = WIDTH//2, HEIGHT//2
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.gap_angles = np.asarray(gap_angles)
        self.gap_widths = gap_widths
        self.gap_line_length = self.thickness * 6
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)

    def draw_gap(self, width, angle, distance, thickness):
        small_angle = math.atan2(distance, width/2)
        poly_distance = int(math.sqrt((width/2)**2 + distance**2))
        sm_distance = poly_distance - thickness//2
        lg_distance = poly_distance + thickness//2 + 50

        lower_angle = angle - 0.025 * width
        upper_angle = angle + 0.025 * width

        p1 = (self.center[0] + int(sm_distance * cos(lower_angle)), self.center[1] + int(sm_distance * sin(lower_angle)))
        p2 = (self.center[0] + int(lg_distance * cos(lower_angle)), self.center[1] + int(lg_distance * sin(lower_angle)))
        p3 = (self.center[0] + int(lg_distance * cos(upper_angle)), self.center[1] + int(lg_distance * sin(upper_angle)))
        p4 = (self.center[0] + int(sm_distance * cos(upper_angle)), self.center[1] + int(sm_distance * sin(upper_angle)))

        return (p1, p2, p3, p4)

    def update(self):
        self.size -= 10
        draw_size = int(self.size + self.pump)
        
        if draw_size <= 0:
            return self.kill()
        self.image.fill(BLACK)
        
        gfxdraw.filled_circle(self.image, *self.center, draw_size//2, WHITE)
        if draw_size//2 > self.thickness:
            gfxdraw.filled_circle(self.image, *self.center, draw_size//2-self.thickness, BLACK)
        
        for width, angle in zip(self.gap_widths, self.gap_angles):
            points = self.draw_gap(width, angle, draw_size//2, self.gap_line_length)
            pygame.draw.polygon(self.image, BLACK, points)

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
s_time_font = freetype.Font('assets/fonts/Bangers-Regular.ttf', 64)
ms_time_font = freetype.Font('assets/fonts/Bangers-Regular.ttf', 32)


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

timer = 0

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

        if random.randrange(5) == 0:
            speed = random.randint(1, 5) / 100
            direction = random.choice((-1, 1))
            screen_rotation_speed = speed * direction

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
            number_of_gaps = random.randint(1, 3)
            angles = [random.random() * 2 * math.pi for _ in range(number_of_gaps)]
            widths = [random.randrange(5) + 10 for _ in range(number_of_gaps)]
            obstacle = Obstacle(angles, widths)
            obstacles.add(obstacle)
        # elif event.type == CHANGE_DIRECTION_EVENT:
        #     if random.randrange(10) == 0:
        #         speed = random.randint(1, 3) / 100
        #         direction = random.choice((-1, 1))
        #         screen_rotation_speed = speed * direction

    for n, obstacle in enumerate(obstacles):
        # if n < 1:
        #     if pygame.sprite.collide_mask(obstacle, player):
        #         sys.exit()
        obstacle.gap_angles += screen_rotation_speed
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

    timer += 1 / FRAMES_PER_SECOND
    seconds = int(timer)
    miliseconds = int((timer % 1) * 1000)

    s_time_font.render_to(screen, (15, 15), f'{seconds}.{miliseconds}', WHITE)


    pygame.display.flip()