from gtts import gTTS
tts = gTTS("Halo Fazril", lang="id")
tts.save("test.mp3")

import pygame
pygame.mixer.init()
pygame.mixer.music.load("test.mp3")
pygame.mixer.music.play()
