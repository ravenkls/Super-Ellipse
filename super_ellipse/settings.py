import pygame
import random
import os

# General Settings
WIDTH = 1280
HEIGHT = 720
ANTIALIASING_ENABLED = False
FRAMES_PER_SECOND = 240
ARROW_SPEED = 0.075

# Music Settings
SONG = os.path.join('assets/music', random.choice(os.listdir('assets/music'))) # 'assets/music/lewis.wav'

# Camera Turn
TURN_CHANGE_CHANCE = 1
LOWEST_TURN_SPEED = 0
HIGHEST_TURN_SPEED = 5

# Timing
OBSTACLE_SPAWN_RATE = 1000 # every X miliseconds
TIMER_UPDATE_INTERVAL = 10 # every X miliseconds
GAME_UPDATE_RATE = 10 # every X miliseconds

# Events
TIMER_UPDATE = pygame.USEREVENT + 1
CREATE_OBSTACLE_EVENT = pygame.USEREVENT + 2
OBSTACLE_SPAWN = pygame.USEREVENT + 3
GAME_UPDATE = pygame.USEREVENT + 4

BACKGROUND_COLOURS = (
    (255, 61, 61), # red
    (255, 164, 61), # orange
    (145, 255, 61), # green
    (61, 255, 187), # blue
    (255, 61, 239) # violet
)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
