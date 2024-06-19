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


def pause_music():
    global current_status
    pygame.mixer.music.pause()
    current_status = "Paused"
    print("Music paused")


def resume_music():
    global current_status, start_time
    pygame.mixer.music.unpause()
    current_status = "Playing"
    start_time = time.time() - (pygame.mixer.music.get_pos() / 1000)
    print("Music resumed")


def stop_music():
    global current_song, current_singer, current_status, start_time, song_length
    pygame.mixer.music.stop()
    current_song = "No music playing"
    current_singer = ""
    current_status = ""
    start_time = 0
    song_length = 0
    print("Music stopped")


def get_song():
    music_folder = "Music"
    songs = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]
    if songs:
        return os.path.join(music_folder, songs[0])
    else:
        return None


def recognize_voice_command(recognizer, microphone):
    with microphone as source:
        print("Listening for command...")
        audio = recognizer.listen(source, timeout=3, phrase_time_limit=2)
        try:
            command = recognizer.recognize_google(audio)
            print("You said : " + command)
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand the audio")
            return None


def handle_voice_command(recognizer, microphone):
    global running
    while running:
        try:
            command = recognize_voice_command(recognizer, microphone)
            if command:
                if "play" in command:
                    song_path = get_song()
                    if song_path:
                        play_music(song_path)
                elif "pause" in command:
                    pause_music()
                elif "resume" in command:
                    resume_music()
                elif "stop" in command:
                    stop_music()
                elif "exit" in command:
                    stop_music()
                    print("Exiting...")
                    running = False
                    break
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")


def draw_progress_bar(surface):
    global current_status, start_time, song_length, previous_progress

    if current_status == "Playing":
        elapsed_time = time.time() - start_time
        progress = min(elapsed_time / song_length, 1.0) if song_length > 0 else 0
        previous_progress = progress
    elif current_status != "Paused":
        progress = 0
    else:
        progress = previous_progress

    pygame.draw.rect(surface, COL1, [10, 90, WIDTH-20, 4], 10)  # Border
    pygame.draw.rect(surface, COL3, [10, 90, (WIDTH-20) * progress, 6], 10)  # Progress bar
    pygame.draw.circle(surface, COL3, (10 + int((WIDTH-20) * progress), 92), 6)


def update_gui():
    # Set background color of the screen
    screen.fill(BACKGROUND)

    # Write song title and singer
    song_text = font1.render(current_song, True, COL2)
    singer_text = font2.render(current_singer, True, COL1)
    screen.blit(song_text, (WIDTH / 2 - len(current_song) * 8, HEIGHT - 130))
    screen.blit(singer_text, (WIDTH / 2 - len(current_singer) * 5, HEIGHT - 100))

    # Draw progress bar
    draw_progress_bar(screen)

    pygame.display.flip()


# Initialize speech recognizer and microphone
recognizer = sr.Recognizer()
microphone = sr.Microphone()

