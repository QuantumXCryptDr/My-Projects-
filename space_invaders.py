#Made By------------------->Voidwalker19<----------------------- Published By#


import pygame
import random

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Set up the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Clone")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load background music
try:
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.play(-1)  # Loop indefinitely
except pygame.error as e:
    print(f"Failed to load background music: {e}")

# Load sounds
try:
    shoot_sound = pygame.mixer.Sound("laser.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")
    power_up_sound = pygame.mixer.Sound("power_up.wav")
    boss_hit_sound = pygame.mixer.Sound("boss_hit.wav")
except FileNotFoundError:
    print("Some sound files not found! Ensure 'laser.wav', 'explosion.wav', 'power_up.wav', and 'boss_hit.wav' are in the folder.")
    shoot_sound = None
    explosion_sound = None
    power_up_sound = None
    boss_hit_sound = None

# Load background
try:
    background = pygame.image.load("background.png").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except FileNotFoundError:
    print("Background image not found! Using black background.")
    background = None

# Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size_level = 1  # 1 = base size, 2 = larger
        self.damage_level = 1  # 1 = base damage, 2 = double damage
        self.update_size_and_damage()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5

    def update_size_and_damage(self):
        try:
            base_image = pygame.image.load("player.png").convert_alpha()
            if self.size_level == 1:
                self.image = pygame.transform.scale(base_image, (150, 150))
            else:  # size_level == 2
                self.image = pygame.transform.scale(base_image, (70, 70))
            if self.damage_level == 2:
                self.image = pygame.transform.flip(self.image, True, False)  # Visual cue for upgrade
        except FileNotFoundError:
            print("Player sprite not found! Using placeholder.")
            self.image = pygame.Surface((50 * self.size_level, 50 * self.size_level))
            self.image.fill(WHITE)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        
# Enemy
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("enemy.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40))
        except FileNotFoundError:
            print("Enemy sprite not found! Using placeholder.")
            self.image = pygame.Surface((40, 40))
            self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.direction = 4
        self.health = 20

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.direction *= -1
            self.rect.y += 20
        if self.rect.bottom > HEIGHT:
            global lives
            lives -= 1
            self.kill()

# Boss
class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("enemyBlack5.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (100, 100))
        except FileNotFoundError:
            print("Boss sprite not found! Using placeholder.")
            self.image = pygame.Surface((100, 100))
            self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.top = 50
        self.speed = 1
        self.health = 50
        self.direction = 4

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.direction *= -1
            self.rect.y += 20
        if self.rect.bottom > HEIGHT:
            global lives
            lives -= 1
            self.kill()

# Bullet
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, damage):
        super().__init__()
        try:
            self.image = pygame.image.load("bullet.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (5 * damage, 10 * damage))  # Scale based on damage
        except FileNotFoundError:
            print("Bullet sprite not found! Using placeholder.")
            self.image = pygame.Surface((5 * damage, 10 * damage))
            self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10
        self.damage = damage

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# PowerUp
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        try:
            self.image = pygame.image.load(f"powerup_star.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (32, 32))  # Scale to a reasonable size
        except FileNotFoundError:
            print(f"Power-up image for {type} not found! Using placeholder.")
            self.image = pygame.Surface((20, 20))
            self.image.fill((0, 255, 0) if type == "size" else (0, 0, 255))  # Fallback to colored squares
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
power_ups = pygame.sprite.Group()
boss = pygame.sprite.GroupSingle()

# Create player
player = Player()
all_sprites.add(player)

# Game variables
enemies_killed = 0
max_enemies = 25
lives = 5
boss_active = False

# Initialize font
try:
    font = pygame.font.Font(None, 36)
except:
    print("Font loading failed! Using fallback.")
    font = pygame.font.SysFont("arial", 36)

# Start menu
game_started = False
start_text = font.render("Press S to Start", True, WHITE)
while not game_started:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            game_started = True
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)
    screen.blit(start_text, (WIDTH // 2 - 100, HEIGHT // 2))
    pygame.display.flip()

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Shoot with Spacebar
                bullet = Bullet(player.rect.centerx, player.rect.top, player.damage_level)
                all_sprites.add(bullet)
                bullets.add(bullet)
                if shoot_sound:
                    shoot_sound.play()
            if event.key == pygame.K_r and (lives <= 0 or (not enemies and not boss)):
                # Reset game
                enemies_killed = 0
                lives = 5
                boss_active = False
                all_sprites.empty()
                enemies.empty()
                bullets.empty()
                enemy_bullets.empty(1)
                power_ups.empty()
                boss.empty()
                player = Player()
                all_sprites.add(player)
                game_started = False  # Return to start menu
                while not game_started:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                            game_started = True
                    if background:
                        screen.blit(background, (0, 0))
                    else:
                        screen.fill(BLACK)
                    screen.blit(start_text, (WIDTH // 2 - 100, HEIGHT // 2))
                    pygame.display.flip()

    # Spawn enemies one by one
    if not boss_active and len(enemies) < 25 and enemies_killed < max_enemies:
        if random.random() < 0.02:  # Chance to spawn a new enemy
            enemy = Enemy(random.randint(0, WIDTH - 40), -40)
            all_sprites.add(enemy)
            enemies.add(enemy)

    # Spawn power-ups randomly
    if random.random() < 0.005 and enemies:
        power_up = PowerUp(random.choice(enemies.sprites()).rect.centerx, random.choice(enemies.sprites()).rect.bottom, random.choice(["size", "damage"]))
        all_sprites.add(power_up)
        power_ups.add(power_up)

    # Activate boss after 25 enemies
    if enemies_killed >= max_enemies and not boss_active:
        boss_active = True
        boss_sprite = Boss()
        all_sprites.add(boss_sprite)
        boss.add(boss_sprite)

    # Enemy shooting
    if random.random() < 0.01:
        if enemies:
            enemy = random.choice(enemies.sprites())
            bullet = Bullet(enemy.rect.centerx, enemy.rect.bottom, 1)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            if shoot_sound:
                shoot_sound.play()
        elif boss:
            bullet = Bullet(boss.sprite.rect.centerx, boss.sprite.rect.bottom, 1)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
            if shoot_sound:
                shoot_sound.play()

    # Update
    all_sprites.update()

    # Collision detection
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        enemies_killed += 1
        if explosion_sound:
            explosion_sound.play()
        if random.random() < 0.3:  # 30% chance to drop power-up
            power_up = PowerUp(hit.rect.centerx, hit.rect.centery, random.choice(["size", "damage"]))
            all_sprites.add(power_up)
            power_ups.add(power_up)

    if boss:
        boss_hits = pygame.sprite.spritecollide(boss.sprite, bullets, True)
        for hit in boss_hits:
            boss.sprite.health -= player.damage_level
            if boss_hit_sound:
                boss_hit_sound.play()
            if boss.sprite.health <= 0:
                boss.sprite.kill()
                if explosion_sound:
                    explosion_sound.play()

    if pygame.sprite.spritecollide(player, enemy_bullets, True):
        lives -= 1
        if explosion_sound:
            explosion_sound.play()

    if pygame.sprite.spritecollide(player, power_ups, True):
        for power in pygame.sprite.spritecollide(player, power_ups, True):
            if power.type == "size" and player.size_level < 2:
                player.size_level += 1
                player.update_size_and_damage()
                if power_up_sound:
                    power_up_sound.play()
            elif power.type == "damage" and player.damage_level < 2:
                player.damage_level += 1
                player.update_size_and_damage()
                if power_up_sound:
                    power_up_sound.play()

    # Draw
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Score and lives display
    score_text = font.render(f"Score: {enemies_killed * 10} Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Game over or boss win screen
    if lives <= 0 or (boss_active and not boss):
        game_over_text = font.render("Game Over! Press R to Restart", True, WHITE) if lives <= 0 else font.render("Boss Defeated! Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    waiting = False
    else:
        pygame.display.flip()

    # Control frame rate
    clock.tick(60)

pygame.quit()