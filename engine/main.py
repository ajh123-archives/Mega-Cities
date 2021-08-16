#!/usr/bin/python3.9
# Setup Python ----------------------------------------------- #
import pygame

# Setup pygame/window ---------------------------------------- #
from pygame.locals import *
from .game import *
from .settings import *


class Menu:
    def __init__(self):
        self.mainClock = pygame.time.Clock()
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

        self.font = pygame.font.SysFont("", 30)
        self.click = False
        self.main_menu()

    @staticmethod
    def draw_text(text, font, color, surface, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def main_menu(self):
        while True:

            self.screen.fill((0, 0, 0))
            self.draw_text('main menu', self.font, (255, 255, 255), self.screen, 20, 20)

            mx, my = pygame.mouse.get_pos()

            button_1 = pygame.Rect(50, 100, 200, 50)
            button_2 = pygame.Rect(50, 200, 200, 50)
            button_3 = pygame.Rect(50, 300, 200, 50)
            if button_1.collidepoint((mx, my)):
                if self.click:
                    self.new_game()
            if button_2.collidepoint((mx, my)):
                if self.click:
                    self.load_game()
            if button_3.collidepoint((mx, my)):
                if self.click:
                    self.options()
            pygame.draw.rect(self.screen, (255, 0, 0), button_1)
            self.draw_text('New Game', self.font, (255, 255, 255), self.screen, 115, 115)
            pygame.draw.rect(self.screen, (255, 0, 0), button_2)
            self.draw_text('Load Game', self.font, (255, 255, 255), self.screen, 115, 215)
            pygame.draw.rect(self.screen, (255, 0, 0), button_3)
            self.draw_text('Options', self.font, (255, 255, 255), self.screen, 115, 315)

            self.click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True

            pygame.display.update()
            self.mainClock.tick(60)

    @staticmethod
    def new_game():
        running = True
        # Create game object.
        g = Game()
        while running:
            g.new()
            # Main Game Loop
            g.run()
            running = g.playing

    @staticmethod
    def load_game():
        running = True
        # Create game object.
        g = Game()
        while running:
            g.load()
            # Main Game Loop
            g.run()
            running = g.playing

    def options(self):
        running = True
        while running:
            self.screen.fill((0, 0, 0))
            self.draw_text('Options', self.font, (255, 255, 255), self.screen, 20, 20)
            self.draw_text('Foo!', self.font, (255, 255, 255), self.screen, 250, 250)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False

            pygame.display.update()
            self.mainClock.tick(60)


m = Menu()
