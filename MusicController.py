import pygame
import speech_recognition as sr
import threading
import time
import os

# Initialize the mixer module in pygame
pygame.mixer.init()

# Initialize pygame for the GUI
pygame.init()
WIDTH = 350
HEIGHT = 150
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voice controlled music player")
font1 = pygame.font.Font(None, 45)
font2 = pygame.font.Font(None, 30)

