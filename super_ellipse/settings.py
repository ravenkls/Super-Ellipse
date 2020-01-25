import pygame

SONG = 'assets/music/eilish.wav'
WIDTH = 1000
HEIGHT = 700
FRAMES_PER_SECOND = 60
ARROW_SPEED = 0.1
OBSTACLE_SPAWN_RATE = 750

CREATE_OBSTACLE_EVENT = pygame.USEREVENT + 1

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