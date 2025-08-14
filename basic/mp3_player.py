# pip install pygame
import pygame, time, sys, os
def play_pygame(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    pygame.mixer.init()
    pygame.mixer.music.load(path)   # mp3, wav 지원
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.05)

if __name__ == "__main__":
    play_pygame("speech_nova.mp3")

