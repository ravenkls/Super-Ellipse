import pygame
from pygame import gfxdraw
from .settings import *
import numpy as np
import math


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
        self.screen_rotation_speed = 0

    def draw_gap(self, width, angle, distance, thickness):
        small_angle = math.atan2(distance, width/2)
        poly_distance = int(math.sqrt((width/2)**2 + distance**2))
        sm_distance = poly_distance - thickness//2
        lg_distance = poly_distance + thickness//2 + 50

        lower_angle = angle - 0.025 * width
        upper_angle = angle + 0.025 * width

        p1 = (self.center[0] + int(sm_distance * math.cos(lower_angle)), self.center[1] + int(sm_distance * math.sin(lower_angle)))
        p2 = (self.center[0] + int(lg_distance * math.cos(lower_angle)), self.center[1] + int(lg_distance * math.sin(lower_angle)))
        p3 = (self.center[0] + int(lg_distance * math.cos(upper_angle)), self.center[1] + int(lg_distance * math.sin(upper_angle)))
        p4 = (self.center[0] + int(sm_distance * math.cos(upper_angle)), self.center[1] + int(sm_distance * math.sin(upper_angle)))

        return (p1, p2, p3, p4)

    def update(self):
        self.size -= 10
        self.gap_angles += self.screen_rotation_speed
        
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
        self.image_file = pygame.image.load('assets/images/arrow.png').convert_alpha()
        self.arrow = pygame.transform.scale(self.image_file, (13, 8))
        self.mask = pygame.mask.from_surface(self.arrow)
        self.pump = 0
        self.image = self.arrow
        self.rect = self.image.get_rect()
        self.center_point = (0, 0)
        self.angle = 0
        self.r = 100
        self.left = 0
        self.right = 0
        self.screen_rotation_speed = 0

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
        self.angle += self.left - self.right - self.screen_rotation_speed
        self.rect.centerx = int(self.center_point[0] + (self.r + self.pump) * math.sin(self.theta))
        self.rect.centery = int(self.center_point[1] + (self.r + self.pump) * math.cos(self.theta))
