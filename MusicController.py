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

BACKGROUND = "#000000"  # Black
COL1 = "#4D4D4D"  # Gray
COL2 = "#FFFFFF"  # White
COL3 = "#B700FF"  # Purple

# Variables to hold the song title, status, and playback time
current_song = "No music playing"
current_singer = ""
current_status = ""
start_time = 0
song_length = 0
previous_progress = 0
running = True


def play_music(file):
    global current_song, current_singer, current_status, start_time, song_length
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    start_time = time.time()
    song_length = pygame.mixer.Sound(file).get_length()

    # Extract song and singer from filename
    file_name = os.path.basename(file).replace('.mp3', '')
    current_song, current_singer = file_name.split(' - ')

    current_status = "Playing"
    print("Playing music...")


