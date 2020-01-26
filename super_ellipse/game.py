import random
import math

import numpy as np
import pygame
import pygame.freetype
import pygame.gfxdraw

from .audio import SongAnalysis
from .settings import *
from .entities import Obstacle, Player


class GameSurface(pygame.Surface):

    def __init__(self, screen):
        self.screen = screen
        self.failed_callback = lambda: None

        # Sounds
        self.gameover_sound = pygame.mixer.Sound('assets/sounds/gameover.wav')

        # Timer Display
        self.time_surface = pygame.Surface((230, 80), pygame.SRCALPHA)
        self.time_font = pygame.freetype.Font('assets/fonts/Square.ttf', 55)
        self.last_obstacle_spawned_at = 0
        self.last_obstacle_update = 0

        # Sprites
        self.obstacles = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()

        self.player = Player()
        self.player.set_center_point(WIDTH//2, HEIGHT//2)
        self.entities.add(self.player)

        self.reset_settings()

        super().__init__(self.screen.get_size())
    
    def reset_settings(self):
        # Remove any obstacles
        for o in self.obstacles:
            o.kill()

        # Timer
        self.timer = 0

        # Movement
        self.left = 0
        self.right = 0
        self.screen_rotation_speed = 0
        self.pump = 0
        self.last_pump = 0

        # Colour
        self.last_colour_change = 0
        self.current_background = np.array([random.choice(BACKGROUND_COLOURS)])

    def set_song(self, filename):
        self.song_file = filename
        self.song = SongAnalysis(filename)
        self.song_length = self.song.duration

    def set_gameover_callback(self, callback):
        self.failed_callback = callback

    def timer_update(self, miliseconds):
        self.timer += miliseconds / 1000

    def update(self):

        self.last_pump = self.pump

        if self.pump > 0:
            self.pump //= 1.1
            self.pump = int(self.pump)
        
        music_pos = pygame.mixer.music.get_pos()
        self.pump = int(max(self.song.calculate_amps(music_pos)[:10]) * 100)
        
        if self.pump >= 45 and self.last_pump <= 45 and self.last_colour_change > 20:
            new_background = self.current_background[0]
            while tuple(new_background) == tuple(self.current_background[0]):
                new_background = random.choice(BACKGROUND_COLOURS)
            self.current_background = np.linspace(self.current_background[0], new_background, int(FRAMES_PER_SECOND * 0.1))
            self.last_colour_change = 0

            if random.randint(1, int(1/TURN_CHANGE_CHANCE)) == 1:
                speed = random.randint(LOWEST_TURN_SPEED, HIGHEST_TURN_SPEED) / 100
                direction = random.choice((-1, 1))
                self.screen_rotation_speed = speed * direction

        for n, obstacle in enumerate(self.obstacles):
            if n < 1:
                if pygame.sprite.collide_mask(obstacle, self.player):
                    pygame.mixer.music.stop()
                    self.reset_settings()
                    return self.failed_callback()
            obstacle.screen_rotation_speed = self.screen_rotation_speed
            obstacle.pump = self.pump

        self.player.screen_rotation_speed = self.screen_rotation_speed
        self.player.left = self.left
        self.player.right = self.right
        self.player.pump = self.pump // 5

        self.fill(self.current_background[0])

        if len(self.current_background) > 1:
            self.current_background = np.delete(self.current_background, 0, axis=0)

        self.last_colour_change += 1

        self.obstacles.draw(self)
        self.entities.draw(self)
        
        if ANTIALIASING_ENABLED:
            pygame.gfxdraw.aacircle(self, WIDTH//2, HEIGHT//2, 60 + self.pump//5, WHITE)
        pygame.gfxdraw.filled_circle(self, WIDTH//2, HEIGHT//2, 60 + self.pump//5, WHITE)

        seconds = int(self.timer)
        miliseconds = int((self.timer % 1) * 100)
        percent = seconds / self.song_length

        if ANTIALIASING_ENABLED:
            pygame.gfxdraw.aapolygon(self.time_surface, ((0, 0),
                                            (self.time_surface.get_width(), 0),
                                            self.time_surface.get_size(),
                                            (40, self.time_surface.get_height())), BLACK)

        pygame.gfxdraw.filled_polygon(self.time_surface, ((0, 0),
                                            (self.time_surface.get_width(), 0),
                                            self.time_surface.get_size(),
                                            (40, self.time_surface.get_height())), BLACK)
        
        pygame.gfxdraw.rectangle(self.time_surface, (55, self.time_surface.get_height()-15, self.time_surface.get_width()-80, 5), self.current_background[0])
        pygame.draw.rect(self.time_surface, self.current_background[0], (55, self.time_surface.get_height()-15, int((self.time_surface.get_width()-80) * percent), 5))

        self.time_font.render_to(self.time_surface, (55, 15), f'{seconds}:{miliseconds}', WHITE)

        self.blit(self.time_surface, (WIDTH - self.time_surface.get_width(), 0))
    
    def move_left(self, amount):
        self.left = amount
    
    def move_right(self, amount):
        self.right = amount
    
    def create_wall(self):
        number_of_gaps = random.randint(1, 3)
        angles = [random.random() * 2 * math.pi for _ in range(number_of_gaps)]
        widths = [random.randrange(5) + 15 for _ in range(number_of_gaps)]
        obstacle = Obstacle(angles, widths)
        self.obstacles.add(obstacle)
