# === INSTALLATION REQUIREMENTS ===
# pip install pygame pillow

import pygame
import random
import time
import os
from PIL import Image

# === CONFIGURATION ===
WIDTH, HEIGHT = 800, 600
PIXEL_SIZE = 4
WAIT_TIME = 5
IMAGE_FOLDER = "images"

# === INITIALIZATION ===
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Rain Tornado Explosion")
clock = pygame.time.Clock()

# === PIXEL OBJECT ===
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
        if new_y >= HEIGHT - PIXEL_SIZE or ground_map[int(self.x / PIXEL_SIZE)][int(new_y / PIXEL_SIZE)]:
            self.landed = True
            self.y = int(self.y / PIXEL_SIZE) * PIXEL_SIZE
            ground_map[int(self.x / PIXEL_SIZE)][int(self.y / PIXEL_SIZE)] = True
        else:
            self.y = new_y

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, PIXEL_SIZE, PIXEL_SIZE))

# === IMAGE HANDLING ===
def load_random_image():
    files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not files:
        raise FileNotFoundError("Aucune image trouvée dans le dossier 'images'.")
    path = os.path.join(IMAGE_FOLDER, random.choice(files))
    print(f"Chargement de l'image : {os.path.basename(path)}")
    return Image.open(path).convert("RGB")

# === IMAGE PIXELATION ===
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

# === PIXEL FALLING EFFECT ===
def destroy_pixels_randomly(pixel_matrix):
    width = len(pixel_matrix[0])
    height = len(pixel_matrix)
    positions = [(x, y) for y in range(height) for x in range(width)]
    random.shuffle(positions)
    falling_pixels = []
    ground_map = [[False for _ in range(HEIGHT // PIXEL_SIZE)] for _ in range(WIDTH // PIXEL_SIZE)]

    batch_size = 100  # Accelerated
    for i in range(0, len(positions), batch_size):
        batch = positions[i:i + batch_size]
        for x, y in batch:
            color = pixel_matrix[y][x]
            falling_pixels.append(Pixel(x * PIXEL_SIZE, y * PIXEL_SIZE, color))
            pixel_matrix[y][x] = None  # leave black

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

    # Ensure all pixels land
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

# === TORNADO EFFECT ===
def run_tornado(pixels):
    direction = random.choice(['left', 'right', 'top', 'bottom'])
    duration = 3.0
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

# === EXPLOSION EFFECT ===
def run_explosion(pixels):
    # Flash blanc intense au départ
    for _ in range(3):
        screen.fill((255, 255, 255))
        pygame.display.flip()
        pygame.time.delay(50)
        screen.fill((0, 0, 0))
        pygame.display.flip()
        pygame.time.delay(50)

    # Initialiser la vitesse et alpha
    for p in pixels:
        p.exploding = True
        p.vx = random.uniform(-30, 30)
        p.vy = random.uniform(-30, 30)
        p.size = PIXEL_SIZE
        p.alpha = 255  # opaque au départ

    frames = 60
    for frame in range(frames):
        screen.fill((0, 0, 0))
        for p in pixels:
            if p.alpha <= 0:
                continue
            # Déplacement avec légère décélération
            decel = 0.9
            p.vx *= decel
            p.vy *= decel
            p.x += p.vx
            p.y += p.vy

            # Pulsation de taille
            pulse = 1 + 0.5 * (1 - frame / frames) * (1 + random.uniform(-0.3, 0.3))
            current_size = max(1, int(p.size * pulse))

            # Réduction progressive de l'alpha
            p.alpha = max(0, p.alpha - int(255 / frames))

            # Créer surface avec alpha
            surf = pygame.Surface((current_size, current_size), pygame.SRCALPHA)
            surf.fill((*p.color, p.alpha))

            screen.blit(surf, (int(p.x), int(p.y)))

        pygame.display.flip()
        clock.tick(60)


# === MAIN LOOP ===
def main():
    while True:
        img = load_random_image()
        pixel_matrix = image_to_pixel_array(img)

        # Afficher l'image complète
        screen.fill((0, 0, 0))
        for y, row in enumerate(pixel_matrix):
            for x, color in enumerate(row):
                pygame.draw.rect(screen, color, (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
        pygame.display.flip()
        time.sleep(WAIT_TIME)

        # Destruction aléatoire + chute
        pixels = destroy_pixels_randomly(pixel_matrix)
        #time.sleep(WAIT_TIME)

        # Tornade
        run_tornado(pixels)
 
        # Explosion finale
        run_explosion(pixels)
       # time.sleep(1)

if __name__ == "__main__":
    main()
