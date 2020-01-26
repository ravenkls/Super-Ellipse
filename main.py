import sys
import pygame

from super_ellipse.settings import *
from super_ellipse.surfaces import GameSurface, MenuSurface

pygame.mixer.init(44100, -16, 2, 512)
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.RESIZABLE)
print('ok')
pygame.display.set_caption('Super Ellipse')
pygame.display.set_icon(pygame.image.load('assets/images/logo.png'))
clock = pygame.time.Clock()

# Timing
pygame.time.set_timer(TIMER_UPDATE, TIMER_UPDATE_INTERVAL)
pygame.time.set_timer(OBSTACLE_SPAWN, OBSTACLE_SPAWN_RATE)
pygame.time.set_timer(GAME_UPDATE, GAME_UPDATE_RATE)

# Surfaces
menu = MenuSurface(screen)

game = GameSurface(screen)
game.set_song(SONG)
game.set_gameover_callback(menu.return_to_menu)


while True:
    clock.tick(FRAMES_PER_SECOND)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.VIDEORESIZE:
            pygame.display.set_mode(event.size)
        elif menu.enabled:
            # MENU CONTROLS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    menu.up()
                elif event.key == pygame.K_DOWN:
                    menu.down()
                elif event.key == pygame.K_RETURN:
                    menu.choose_option()
        else:
            # GAME CONTROLS
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_left(ARROW_SPEED)
                elif event.key == pygame.K_RIGHT:
                    game.move_right(ARROW_SPEED)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    game.move_left(0)
                elif event.key == pygame.K_RIGHT:
                    game.move_right(0)
            elif event.type == TIMER_UPDATE:
                game.timer_update(TIMER_UPDATE_INTERVAL)
            elif event.type == OBSTACLE_SPAWN:
                game.create_wall()
            elif event.type == GAME_UPDATE:
                game.obstacles.update()
                game.entities.update()

    if menu.enabled:
        menu.update()
        screen.blit(menu, (0, 0))
    else:
        game.update()
        screen.blit(game, (0, 0))

        if not pygame.mixer.music.get_busy() and not menu.enabled:
            pygame.mixer.music.load(game.song_file)
            pygame.mixer.music.play(-1)
        
    pygame.display.flip()
