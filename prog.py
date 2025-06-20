import pygame
import random
import time
import os
import hashlib
import numpy as np
from PIL import Image
import threading

# Initialisation de pygame et du mixer
pygame.init()
pygame.mixer.init()

# Dimensions de l'écran et autres constantes
WIDTH, HEIGHT = 800, 600
PIXEL_SIZE = 4
WAIT_TIME = 5
IMAGE_FOLDER = "images"

# Fréquences des notes de musique
note_frequencies = {
    'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
    'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
    'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88,
    'C6': 523.25, 'C#6': 554.37, 'D6': 587.33, 'D#6': 622.25
}

class Pixel:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = 0
        self.vy = 0
        self.landed = False
        self.flying = False
        self.exploding = False
        self.size = PIXEL_SIZE
        self.alpha = 255

    def update(self, ground_map):
        if self.exploding:
            self.x += random.randint(-15, 15)
            self.y += random.randint(-15, 15)
            return
        if self.flying:
            self.x += random.randint(-10, 10)
            self.y += random.randint(-10, 10)
            return
        if self.landed:
            return
        self.vy += 0.5
        new_y = self.y + self.vy
        if new_y >= HEIGHT - PIXEL_SIZE or (ground_map and ground_map[int(self.x / PIXEL_SIZE)][int(new_y / PIXEL_SIZE)]):
            self.landed = True
            self.y = int(self.y / PIXEL_SIZE) * PIXEL_SIZE
            if ground_map:
                ground_map[int(self.x / PIXEL_SIZE)][int(self.y / PIXEL_SIZE)] = True
        else:
            self.y = new_y

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, PIXEL_SIZE, PIXEL_SIZE))

def load_random_image():
    files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not files:
        raise FileNotFoundError("Aucune image trouvée dans le dossier 'images'.")
    path = os.path.join(IMAGE_FOLDER, random.choice(files))
    print(f"Chargement de l'image : {os.path.basename(path)}")
    return Image.open(path).convert("RGB")

def image_to_pixel_array(img):
    img = img.resize((WIDTH // PIXEL_SIZE, HEIGHT // PIXEL_SIZE))
    pixels = []
    data = img.load()
    for y in range(img.height):
        row = []
        for x in range(img.width):
            row.append(data[x, y])
        pixels.append(row)
    return pixels

def destroy_pixels_randomly(pixel_matrix, screen, clock):
    width = len(pixel_matrix[0])
    height = len(pixel_matrix)
    positions = [(x, y) for y in range(height) for x in range(width)]
    random.shuffle(positions)
    falling_pixels = []
    ground_map = [[False for _ in range(HEIGHT // PIXEL_SIZE)] for _ in range(WIDTH // PIXEL_SIZE)]
    batch_size = 100
    for i in range(0, len(positions), batch_size):
        batch = positions[i:i + batch_size]
        for x, y in batch:
            color = pixel_matrix[y][x]
            falling_pixels.append(Pixel(x * PIXEL_SIZE, y * PIXEL_SIZE, color))
            pixel_matrix[y][x] = None
        screen.fill((0, 0, 0))
        for row_idx, row in enumerate(pixel_matrix):
            for col_idx, color in enumerate(row):
                if color:
                    pygame.draw.rect(screen, color, (col_idx * PIXEL_SIZE, row_idx * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
        for p in falling_pixels:
            p.update(ground_map)
            p.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    all_landed = False
    while not all_landed:
        all_landed = True
        screen.fill((0, 0, 0))
        for row_idx, row in enumerate(pixel_matrix):
            for col_idx, color in enumerate(row):
                if color:
                    pygame.draw.rect(screen, color, (col_idx * PIXEL_SIZE, row_idx * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
        for p in falling_pixels:
            p.update(ground_map)
            if not p.landed:
                all_landed = False
            p.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    return falling_pixels

def run_tornado(pixels, screen, clock):
    direction = random.choice(['left', 'right', 'top', 'bottom'])
    steps = 100
    for step in range(steps):
        screen.fill((0, 0, 0))
        threshold = 0
        if direction == 'left':
            threshold = WIDTH * (step / steps)
            for p in pixels:
                if not p.flying and p.x < threshold:
                    p.flying = True
        elif direction == 'right':
            threshold = WIDTH * (1 - step / steps)
            for p in pixels:
                if not p.flying and p.x > threshold:
                    p.flying = True
        elif direction == 'top':
            threshold = HEIGHT * (step / steps)
            for p in pixels:
                if not p.flying and p.y < threshold:
                    p.flying = True
        elif direction == 'bottom':
            threshold = HEIGHT * (1 - step / steps)
            for p in pixels:
                if not p.flying and p.y > threshold:
                    p.flying = True
        for p in pixels:
            p.update(None)
            p.draw(screen)
        pygame.display.flip()
        clock.tick(60)

def run_explosion(pixels, screen, clock):
    for _ in range(3):
        screen.fill((255, 255, 255))
        pygame.display.flip()
        pygame.time.delay(50)
        screen.fill((0, 0, 0))
        pygame.display.flip()
        pygame.time.delay(50)

    for p in pixels:
        p.exploding = True
        p.vx = random.uniform(-30, 30)
        p.vy = random.uniform(-30, 30)
        p.size = PIXEL_SIZE
        p.alpha = 255

    frames = 60
    for frame in range(frames):
        screen.fill((0, 0, 0))
        for p in pixels:
            if p.alpha <= 0:
                continue
            decel = 0.9
            p.vx *= decel
            p.vy *= decel
            p.x += p.vx
            p.y += p.vy
            pulse = 1 + 0.5 * (1 - frame / frames) * (1 + random.uniform(-0.3, 0.3))
            current_size = max(1, int(p.size * pulse))
            p.alpha = max(0, p.alpha - int(255 / frames))
            surf = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
            surf.fill((*p.color, p.alpha))
            screen.blit(surf, (int(p.x), int(p.y)))
        pygame.display.flip()
        clock.tick(60)

def calculate_sha512(file_path):
    sha512_hash = hashlib.sha512()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha512_hash.update(byte_block)
    return sha512_hash.hexdigest()

def sha512_to_melody_and_rhythm(sha512_hash):
    note_map = {
        '0': 'C', '1': 'C#', '2': 'D', '3': 'D#',
        '4': 'E', '5': 'F', '6': 'F#', '7': 'G',
        '8': 'G#', '9': 'A', 'a': 'A#', 'b': 'B',
        'c': 'C6', 'd': 'C#6', 'e': 'D6', 'f': 'D#6'
    }
    duration_map = {
        '0': 0.05, '1': 0.1, '2': 0.15, '3': 0.2,
        '4': 0.25, '5': 0.3, '6': 0.35, '7': 0.4,
        '8': 0.45, '9': 0.5, 'a': 0.075, 'b': 0.125,
        'c': 0.175, 'd': 0.225, 'e': 0.275, 'f': 0.325
    }
    melody = []
    rhythm = []
    for i in range(0, len(sha512_hash), 2):
        char = sha512_hash[i]
        melody.append(note_map.get(char, 'Rest'))
        if i + 1 < len(sha512_hash):
            duration_char = sha512_hash[i + 1]
            rhythm.append(('note', duration_map.get(duration_char, 0.2)))
        else:
            rhythm.append(('note', 0.2))
    return melody, rhythm

def play_melody(melody, rhythm):
    for i, (note_type, duration) in enumerate(rhythm):
        if note_type == 'note':
            current_note = melody[i]
            if current_note != 'Rest':
                frequency = note_frequencies[current_note]
                sample_rate = 44100
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                wave = 4096 * np.sin(2 * np.pi * frequency * t)
                wave = np.column_stack((wave, wave)).astype(np.int16)
                sound = pygame.sndarray.make_sound(wave)
                sound.play()
                while pygame.mixer.get_busy():
                    time.sleep(0.01)
            else:
                time.sleep(duration)

def main():
    try:
        print("Début du programme")
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        print("Fenêtre Pygame initialisée")
        pygame.display.set_caption("Pixel Rain Tornado Explosion with Music")
        clock = pygame.time.Clock()

        while True:
            print("Chargement d'une nouvelle image")
            img = load_random_image()
            img_path = os.path.join(IMAGE_FOLDER, random.choice([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]))
            sha512_hash = calculate_sha512(img_path)
            melody, rhythm = sha512_to_melody_and_rhythm(sha512_hash)

            print("Affichage de l'image")
            screen.fill((0, 0, 0))
            pixel_matrix = image_to_pixel_array(img)
            for y, row in enumerate(pixel_matrix):
                for x, color in enumerate(row):
                    pygame.draw.rect(screen, color, (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
            pygame.display.flip()
            time.sleep(WAIT_TIME)

            print("Lecture de la mélodie")
            melody_thread = threading.Thread(target=play_melody, args=(melody, rhythm))
            melody_thread.start()

            print("Exécution des animations")
            pixels = destroy_pixels_randomly(pixel_matrix, screen, clock)
            run_tornado(pixels, screen, clock)
            run_explosion(pixels, screen, clock)

            print("Attente de la fin de la mélodie")
            melody_thread.join()
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

if __name__ == "__main__":
    main()
