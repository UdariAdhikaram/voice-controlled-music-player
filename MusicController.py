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
font3 = pygame.font.Font(None, 25)

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

# List to store songs and current song index
songs = []
current_song_index = -1

# Initialize volume
current_volume = 0.5  # Default volume level (50%)
volume_display_time = 2  # Time to display volume level in seconds
volume_display_start = 0

def load_songs():
    global songs
    music_folder = "Music"
    songs = [os.path.join(music_folder, f) for f in os.listdir(music_folder) if f.endswith('.mp3')]

def play_music(index):
    global current_song, current_singer, current_status, start_time, song_length, current_song_index
    if index < 0 or index >= len(songs):
        print("Invalid song index")
        return

    file = songs[index]
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(current_volume)  # Set initial volume
    start_time = time.time()
    song_length = pygame.mixer.Sound(file).get_length()

    # Extract song and singer from filename
    file_name = os.path.basename(file).replace('.mp3', '')
    if '-' in file_name:
        current_song, current_singer = file_name.split('-', 1)
    else:
        current_song = file_name
        current_singer = "Unknown"

    current_status = "Playing"
    current_song_index = index
    print("Playing music...")

def halt_music():
    global current_status
    pygame.mixer.music.pause()
    current_status = "Halt"
    print("Music paused.")

def resume_music():
    global current_status, start_time
    pygame.mixer.music.unpause()
    current_status = "Playing"
    start_time = time.time() - (pygame.mixer.music.get_pos() / 1000)
    print("Music resumed.")

def stop_music():
    global current_song, current_singer, current_status, start_time, song_length
    pygame.mixer.music.stop()
    current_song = "No music playing"
    current_singer = ""
    current_status = ""
    start_time = 0
    song_length = 0
    print("Music stopped.")

def next_song():
    global current_song_index
    if current_song_index < len(songs) - 1:
        play_music(current_song_index + 1)
    else:
        print("No next song available")

def previous_song():
    global current_song_index
    if current_song_index > 0:
        play_music(current_song_index - 1)
    else:
        print("No previous song available")

def volume_up():
    global current_volume, volume_display_start
    current_volume = min(current_volume + 0.1, 1.0)  # Increase volume by 10%
    pygame.mixer.music.set_volume(current_volume)
    volume_display_start = time.time()
    print(f"Volume increased to {current_volume * 100:.0f}%")

def volume_down():
    global current_volume, volume_display_start
    current_volume = max(current_volume - 0.1, 0.0)  # Decrease volume by 10%
    pygame.mixer.music.set_volume(current_volume)
    volume_display_start = time.time()
    print(f"Volume decreased to {current_volume * 100:.0f}%")

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
                    if songs:
                        play_music(0)
                elif "halt" in command:
                    halt_music()
                elif "resume" in command:
                    resume_music()
                elif "stop" in command:
                    stop_music()
                elif "next" in command:
                    next_song()
                elif "previous" in command:
                    previous_song()
                elif "volume up" in command:
                    volume_up()
                elif "volume down" in command:
                    volume_down()
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
    global current_status, start_time, song_length, previous_progress, progress

    if current_status == "Playing":
        elapsed_time = time.time() - start_time
        progress = min(elapsed_time / song_length, 1.0) if song_length > 0 else 0
        previous_progress = progress
    elif current_status != "Halt":
        progress = 0
    else:
        progress = previous_progress

    pygame.draw.rect(surface, COL1, [10, 90, WIDTH - 20, 4], 10)  # Border
    pygame.draw.rect(surface, COL3, [10, 90, (WIDTH - 20) * progress, 6], 10)  # Progress bar
    pygame.draw.circle(surface, COL3, (10 + (WIDTH - 20) * progress, 92), 6)

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

    current_status_symbol = ">" if current_status != "Playing" else "||"
    status_time = font1.render(current_status_symbol, True, COL2)
    screen.blit(status_time, (WIDTH / 2 - 7, HEIGHT - 40))

    # Display volume level if recently changed
    if time.time() - volume_display_start < volume_display_time:
        volume_text = font3.render(f"Volume: {int(current_volume * 100)}%", True, COL2)
        screen.blit(volume_text, (10, 10))

    pygame.display.flip()

# Load the songs
load_songs()

# Initialize speech recognizer and microphone
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Run the voice command handler in a separate thread
voice_thread = threading.Thread(target=handle_voice_command, args=(recognizer, microphone))
voice_thread.start()

# Main loop for the GUI
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_gui()

pygame.quit()
