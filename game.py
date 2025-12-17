# Importando bibliotecas

import pgzrun
import random

WIDTH = 800
HEIGHT = 600

# Game States
MENU = 'menu'
PLAYING = 'playing'
CONGRATS = 'congrats'
game_state = MENU

# Sound Control
sound_on = True

# Stage and Life
stage = 1
life = 3

# Background Music
music.set_volume(0.5)
music.play('background_music')

# Hero Class
class Hero(Actor):
    def __init__(self, pos):
        super().__init__('hero_idle1', pos)
        self.images_idle = ['hero_idle1', 'hero_idle2']
        self.images_walk = ['hero_walk1', 'hero_walk2']
        self.frame = 0
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.anim_timer = 0

    def update(self):
        self.vy += 0.5  # Gravity
        self.y += self.vy
        self.x += self.vx

        # Ground collision
        if self.y > HEIGHT - 50:
            self.y = HEIGHT - 50
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Screen boundaries
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, self.y)

        # Animation
        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.frame = (self.frame + 1) % len(self.images_idle)
            self.anim_timer = 0

        if self.vx != 0:
            self.image = self.images_walk[self.frame % len(self.images_walk)]
        else:
            self.image = self.images_idle[self.frame % len(self.images_idle)]

# Enemy Class
class Enemy(Actor):
    def __init__(self, pos, patrol_range):
        super().__init__('enemy_idle1', pos)
        self.images_idle = ['enemy_idle1', 'enemy_idle2']
        self.images_walk = ['enemy_walk1', 'enemy_walk2']
        self.frame = 0
        self.vx = 2
        self.vy = 0
        self.on_ground = False
        self.patrol_range = patrol_range
        self.start_x = pos[0]
        self.anim_timer = 0

    def update(self):
        # Horizontal movement
        self.x += self.vx
        if abs(self.x - self.start_x) > self.patrol_range:
            self.vx *= -1

        # Random jump
        if self.on_ground and random.random() < 0.01:
            self.vy = -15

        # Gravity
        self.vy += 0.5
        self.y += self.vy

        # Ground collision
        if self.y > HEIGHT - 50:
            self.y = HEIGHT - 50
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Animation
        self.anim_timer += 1
        if self.anim_timer >= 10:
            self.frame = (self.frame + 1) % len(self.images_idle)
            self.anim_timer = 0

        if self.vx != 0:
            self.image = self.images_walk[self.frame % len(self.images_walk)]
        else:
            self.image = self.images_idle[self.frame % len(self.images_idle)]

# Initialize game objects
hero = Hero((50, HEIGHT - 50))
enemies = []

# Button variables
button_hover = None

def spawn_enemies():
    global enemies
    if stage == 1:
        enemies = [Enemy((400, HEIGHT - 50), 100)]
    elif stage == 2:
        enemies = [Enemy((400, HEIGHT - 50), 100), Enemy((600, HEIGHT - 50), 100)]
    elif stage == 3:
        enemies = [Enemy((400, HEIGHT - 50), 120), Enemy((650, HEIGHT - 50), 120), Enemy((700, HEIGHT - 50), 80)]

def draw():
    screen.clear()
    screen.blit('background', (0, 0))

    # Draw ground
    screen.draw.filled_rect(Rect((0, HEIGHT - 50), (WIDTH, 50)), (139, 69, 19))

    # Draw road
    road_height = 30
    road_y = HEIGHT - 50 + (50 - road_height) // 2
    screen.draw.filled_rect(Rect((0, road_y), (WIDTH, road_height)), (50, 50, 50))

    # Road stripes
    stripe_width, stripe_height, gap = 40, 4, 20
    for x in range(0, WIDTH, stripe_width + gap):
        screen.draw.filled_rect(Rect((x, road_y + road_height//2 - stripe_height//2),
                                    (stripe_width, stripe_height)), (255, 255, 255))

    if game_state == MENU:
        screen.draw.text("RUNNING ADVENTURE",
                         center=(WIDTH//2, HEIGHT//4),
                         fontsize=60,
                         color="white",
                         shadow=(1,1),
                         scolor="black")

        # Start button
        color_start = (100, 255, 100) if button_hover == "start" else (0, 200, 0)
        screen.draw.filled_rect(Rect((WIDTH//2 - 100, HEIGHT//2 - 70), (200, 50)), color_start)
        screen.draw.text("START",
                         center=(WIDTH//2, HEIGHT//2 - 45),
                         fontsize=40,
                         color="white")

        # Sound button
        sound_text = "SOUND: ON" if sound_on else "SOUND: OFF"
        color_sound = (100, 100, 255) if button_hover == "sound" else (0, 0, 200)
        screen.draw.filled_rect(Rect((WIDTH//2 - 100, HEIGHT//2), (200, 50)), color_sound)
        screen.draw.text(sound_text,
                         center=(WIDTH//2, HEIGHT//2 + 25),
                         fontsize=40,
                         color="white")

        # Exit button
        color_exit = (255, 100, 100) if button_hover == "exit" else (200, 0, 0)
        screen.draw.filled_rect(Rect((WIDTH//2 - 100, HEIGHT//2 + 70), (200, 50)), color_exit)
        screen.draw.text("EXIT",
                         center=(WIDTH//2, HEIGHT//2 + 95),
                         fontsize=40,
                         color="white")

    elif game_state == PLAYING:
        hero.draw()
        for enemy in enemies:
            enemy.draw()

        screen.draw.text(f"Stage: {stage} - Life: {life}", (10, 10), fontsize=30, color="white")

    elif game_state == CONGRATS:
        screen.draw.text("CONGRATULATIONS!",
                         center=(WIDTH//2, HEIGHT//2),
                         fontsize=60,
                         color="yellow",
                         shadow=(1,1),
                         scolor="black")

def update():
    if game_state == PLAYING:
        hero.update()
        for enemy in enemies:
            enemy.update()

        # Collision detection
        for enemy in enemies:
            if hero.colliderect(enemy):
                if sound_on:
                    sounds.hit.play()
                handle_life_loss()

        # Check if player reached the right end
        if hero.x >= WIDTH - 10:
            next_stage()

def handle_life_loss():
    global life
    life -= 1
    if life <= 0:
        reset_game()
    else:
        reset_stage()

def next_stage():
    global stage, game_state
    stage += 1
    if stage > 3:
        game_state = CONGRATS
    else:
        reset_stage()

def reset_stage():
    global hero
    hero = Hero((50, HEIGHT - 50))
    spawn_enemies()

def reset_game():
    global stage, life, game_state
    stage = 1
    life = 3
    game_state = MENU
    if sound_on:
        music.play('background_music')

def on_key_down(key):
    if game_state == PLAYING:
        if key == keys.LEFT:
            hero.vx = -5
        elif key == keys.RIGHT:
            hero.vx = 5
        elif key == keys.SPACE and hero.on_ground:
            hero.vy = -20
            if sound_on:
                sounds.jump.play()

def on_key_up(key):
    if game_state == PLAYING:
        if key in (keys.LEFT, keys.RIGHT):
            hero.vx = 0

def on_mouse_down(pos):
    global game_state, sound_on
    x, y = pos
    if game_state == MENU:
        if WIDTH//2 - 100 <= x <= WIDTH//2 + 100:
            if HEIGHT//2 - 70 <= y <= HEIGHT//2 - 20:
                game_state = PLAYING
                reset_stage()
                music.stop()
            elif HEIGHT//2 <= y <= HEIGHT//2 + 50:
                sound_on = not sound_on
                if sound_on:
                    music.play('background_music')
                else:
                    music.stop()
            elif HEIGHT//2 + 70 <= y <= HEIGHT//2 + 120:
                exit()

def on_mouse_move(pos):
    global button_hover
    x, y = pos
    button_hover = None
    if WIDTH//2 - 100 <= x <= WIDTH//2 + 100:
        if HEIGHT//2 - 70 <= y <= HEIGHT//2 - 20:
            button_hover = "start"
        elif HEIGHT//2 <= y <= HEIGHT//2 + 50:
            button_hover = "sound"
        elif HEIGHT//2 + 70 <= y <= HEIGHT//2 + 120:
            button_hover = "exit"

pgzrun.go()
