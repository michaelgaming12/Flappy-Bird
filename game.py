import pygame
import sys
import time
import random
import os

# Initialize pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 600, 800
FPS = 120
gravity = 0.22
vertical_speed = -7

# Colors
WHITE = (255, 255, 255)

# Set up paths for images
IMAGES_PATH = os.path.join(os.getcwd(), "assets/images")
FONTS_PATH = os.path.join(os.getcwd(), "assets/fonts")
SOUNDS_PATH = os.path.join(os.getcwd(), "assets/audio")

# Initialize the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Load images
back_img = pygame.image.load(os.path.join(IMAGES_PATH, "background.png"))
back_img = pygame.transform.scale(back_img, (WIDTH, HEIGHT))

floor_img = pygame.image.load(os.path.join(IMAGES_PATH, "ground.png"))
floor_img = pygame.transform.scale(floor_img, (WIDTH, floor_img.get_height()))

bird_images = [pygame.image.load(os.path.join(IMAGES_PATH, f"img_{i}.png")) for i in range(47, 50)]
pipe_img = pygame.image.load(os.path.join(IMAGES_PATH, "pipe.png"))
over_img = pygame.image.load(os.path.join(IMAGES_PATH, "title.png")).convert_alpha()

# Load fonts
score_font = pygame.font.Font(os.path.join(FONTS_PATH, "regular.ttf"), 37)

# Load sound effects
cross_pipe_sound = pygame.mixer.Sound(os.path.join(SOUNDS_PATH, "cross_pipe.mp3"))
cross_pipe_sound.set_volume(0.5)

death_sound = pygame.mixer.Sound(os.path.join(SOUNDS_PATH, "death.mp3"))
death_sound.set_volume(0.3)

# Play the background music
pygame.mixer.music.load(os.path.join(SOUNDS_PATH, "bg.mp3"))
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

# Game variables
bird_index = 0
bird_img = bird_images[bird_index]
bird_rect = bird_img.get_rect(center=(67, HEIGHT // 2))
bird_movement = 0
pipes = []
pipe_heights = [302, 350, 377, 409, 436, 490, 508, 553]
floor_x = 0
score = 0
game_over = False
score_time = True
bird_flap = pygame.USEREVENT
pygame.time.set_timer(bird_flap, 200)
create_pipe = pygame.USEREVENT + 1
pygame.time.set_timer(create_pipe, 1200)
level = 1

# High scores data
high_scores = []

def load_high_scores():
    global high_scores
    try:
        with open("high_scores.txt", "r") as file:
            for line in file:
                data = line.strip().split(",")
                if len(data) == 2:
                    name, score = data
                    high_scores.append((name, int(score)))
                else:
                    print("Invalid format in high_scores.txt. Skipping line:", line)
    except FileNotFoundError:
        pass

def save_high_scores():
    sorted_high_scores = sorted(high_scores, key=lambda x: x[1], reverse=True)
    with open("high_scores.txt", "w") as file:
        for i, (name, score) in enumerate(sorted_high_scores, start=1):
            file.write(f"{i}. {name}, {score}\n")

def reset_game():
    global bird_movement, pipes, bird_rect, score, score_time, game_over, level

    game_over = False
    pipes = []
    bird_movement = 0
    bird_rect = bird_img.get_rect(center=(67, HEIGHT // 2))
    score_time = True
    score = 0
    level = 1


def handle_input():
    global bird_movement, game_over

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_scores()
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bird_movement = vertical_speed

            if event.key == pygame.K_SPACE and game_over:
                reset_game()

            # Close the game if the Escape key is pressed
            if event.key == pygame.K_ESCAPE:
                save_high_scores()
                pygame.quit()
                sys.exit()

        if event.type == bird_flap:
            flap_bird()

        if event.type == create_pipe:
            pipes.extend(create_pipes())


def flap_bird():
    global bird_index, bird_img, bird_rect

    bird_index = (bird_index + 1) % 3
    bird_img = bird_images[bird_index]
    bird_rect = bird_img.get_rect(center=bird_rect.center)


def update_bird():
    global bird_movement, game_over, bird_rect

    if not game_over:
        bird_movement += gravity
        bird_rect.centery += bird_movement
        rotated_bird = pygame.transform.rotozoom(bird_img, bird_movement * -6, 1)

        if bird_rect.top < 0 or bird_rect.bottom >= HEIGHT - floor_img.get_height():
            game_over = True

        screen.blit(rotated_bird, bird_rect)

def update_pipes():
    global pipes, game_over

    pipe_speed = level + 2

    for pipe in pipes:
        # Move the pipe horizontally
        pipe.centerx -= pipe_speed

        flipped_pipe = pygame.transform.flip(pipe_img, False, True) if pipe.top < 0 else pipe_img
        screen.blit(flipped_pipe, pipe)

        # Check for collision with the bird
        if bird_rect.colliderect(pipe):
            game_over = True
            death_sound.play()

    # Remove pipes that have moved off the screen
    pipes = [pipe for pipe in pipes if pipe.right > 0]

def update_score():
    global score, score_time, game_over, level

    if not game_over and pipes:
        # Check if the bird has passed the current set of pipes
        if pipes[0].right < bird_rect.centerx and score_time:
            score += 1
            if score % 10 == 0:
                level += 1  # Increase level every 10 points
            score_time = False

            # Play sound effect for crossing a pipe
            cross_pipe_sound.play()

        # Reset score_time if the bird is before the current set of pipes
        if bird_rect.centerx < pipes[0].left:
            score_time = True

    if game_over and score > 0:
        if (player_name, score) not in high_scores:
            high_scores.append((player_name, score))


def draw_score(game_state):
    score_text = score_font.render(f"Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 66))
    screen.blit(score_text, score_rect)

    level_text = score_font.render(f"Level: {level}", True, WHITE)
    level_rect = level_text.get_rect(center=(WIDTH // 2, 100))
    screen.blit(level_text, level_rect)

    if game_state == "game_over":
        pass


def draw_floor():
    screen.blit(floor_img, (floor_x, HEIGHT - floor_img.get_height()))
    screen.blit(floor_img, (floor_x + floor_img.get_width(), HEIGHT - floor_img.get_height()))


def create_pipes():
    top_pipe = pipe_img.get_rect(midbottom=(0, 0))
    bottom_pipe = pipe_img.get_rect(midtop=(0, 0))
    pipe_y = random.choice(pipe_heights)
    top_pipe.midbottom = (WIDTH, pipe_y - 300)
    bottom_pipe.midtop = (WIDTH, pipe_y)
    return top_pipe, bottom_pipe


def get_player_name():
    player_name = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        font = pygame.font.Font("assets/fonts/regular.ttf", 36)
        text = font.render(f"Enter your name: {player_name}", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
        pygame.display.flip()

    # Set default name to 'Anonymous' if player entered nothing or just spaces
    if not player_name.strip():
        player_name = 'Anonymous'

    return player_name.strip()


# Load high scores when starting the game
load_high_scores()

# Prompt the player to enter their name before starting the game
player_name = get_player_name()

# Game loop
running = True
while running:
    clock.tick(FPS)

    handle_input()

    screen.blit(back_img, (0, 0))
    screen.blit(floor_img, (floor_x, HEIGHT - floor_img.get_height()))

    update_bird()
    update_pipes()
    update_score()
    draw_score("game_on")

    if game_over:
        screen.blit(over_img, (WIDTH // 2 - over_img.get_width() // 2, HEIGHT // 2 - over_img.get_height() // 2))
        draw_score("game_over")
        if score > 10:  # Save high score only if the player scored 10 or above
            save_high_scores()  # Save high scores when the game is over

    floor_x -= 1
    if floor_x < -floor_img.get_width():
        floor_x = 0

    draw_floor()

    pygame.display.update()

pygame.quit()
sys.exit()
