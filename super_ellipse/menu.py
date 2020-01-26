import pygame
import pygame.freetype
import numpy as np
import itertools
from .settings import *


class MenuSurface(pygame.Surface):

    def __init__(self, screen):
        self.screen = screen
        self.background_cycle = itertools.cycle(BACKGROUND_COLOURS)
        self.background_transition = np.array([next(self.background_cycle)])
        self.button_font = pygame.freetype.Font('assets/fonts/Square.ttf', 24)
        self.title_font = pygame.freetype.Font('assets/fonts/Square.ttf', 74)
        self.buttons = ['PLAY', 'SONGS', 'SETTINGS', 'QUIT']
        self.option_change_sound = pygame.mixer.Sound('assets/sounds/option_change.wav')
        self.option_confirm_sound = pygame.mixer.Sound('assets/sounds/option_confirm.wav')
        self.current_index = 0
        self.enabled = True
        super().__init__(self.screen.get_size())

    def update(self):
        if self.background_transition.size == 3:
            self.background_transition = np.linspace(self.background_transition[0], next(self.background_cycle), 500)

        title, title_rect = self.title_font.render('Super Ellipse', WHITE)

        self.fill(self.background_transition[0])

        for n, button_text in enumerate(self.buttons):
            selected = (n == self.current_index)
            play_button = self.create_button(button_text, selected=selected)
            self.blit(play_button, (WIDTH//2 - play_button.get_width()//2, 275 + 65*n))

        self.blit(title, (WIDTH//2 - title_rect.width//2, 150))
        self.background_transition = np.delete(self.background_transition, 0, axis=0)

    def create_button(self, button_text, selected=False):
        width, height = 300, 50
        button = pygame.Surface((width, height))
        if selected:
            button.fill(BLACK)
            button_text, button_text_rect = self.button_font.render(button_text, WHITE)
        else:
            button.fill(WHITE)
            button_text, button_text_rect = self.button_font.render(button_text, BLACK)
        
        button.blit(button_text, (width//2 - button_text_rect.width//2, height//2 - button_text_rect.height//2))

        return button
    
    def down(self):
        self.current_index += 1
        if self.current_index == len(self.buttons):
            self.current_index = 0
        self.option_change_sound.play()
    
    def up(self):
        self.current_index -= 1
        if self.current_index == -1:
            self.current_index = len(self.buttons) - 1
        self.option_change_sound.play()
    
    def choose_option(self):
        self.option_confirm_sound.play()
        option = self.buttons[self.current_index]
        if option == 'PLAY':
            self.enabled = False
        
    def return_to_menu(self):
        self.enabled = True
