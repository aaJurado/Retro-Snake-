import os
import random
import sys

import pygame


# ============================================================
# Retro Snake Arcade
# Author: Axel Lucero
# Description:
# A retro-style Snake game built with Python and pygame.
# Features include a start menu, difficulty selection,
# collision detection, score tracking, pause/resume, and
# persistent high score storage.
# ============================================================


# -----------------------------
# Game Constants
# -----------------------------

CELL_SIZE = 25
GRID_WIDTH = 24
GRID_HEIGHT = 20

HEADER_HEIGHT = 80

SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT + HEADER_HEIGHT

HIGH_SCORE_FILE = "high_score.txt"

# Difficulty speeds
EASY_SPEED = 8
MEDIUM_SPEED = 12
HARD_SPEED = 16

# Colors
BLACK = (10, 10, 10)
DARK_GREEN = (0, 70, 0)
GREEN = (0, 220, 90)
LIGHT_GREEN = (120, 255, 150)
RED = (255, 65, 65)
WHITE = (240, 240, 240)
YELLOW = (255, 225, 90)
GRAY = (110, 110, 110)
BLUE = (90, 170, 255)


# -----------------------------
# pygame Setup
# -----------------------------

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Retro Snake Arcade")

clock = pygame.time.Clock()

font_small = pygame.font.SysFont("consolas", 22)
font_medium = pygame.font.SysFont("consolas", 34)
font_large = pygame.font.SysFont("consolas", 54)


# -----------------------------
# File Handling
# -----------------------------

def load_high_score():
    """
    Reads the saved high score from a text file.
    If the file does not exist or contains invalid data,
    the high score starts at 0.
    """
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0

    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            content = file.read().strip()

            if content.isdigit():
                return int(content)

    except OSError:
        return 0

    return 0


def save_high_score(score):
    """
    Saves the high score to a text file.
    """
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(score))
    except OSError:
        pass


# -----------------------------
# Drawing Functions
# -----------------------------

def draw_text(text, font, color, x, y, center=True):
    """
    Draws text on the screen.
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    screen.blit(text_surface, text_rect)


def draw_header(score, high_score, difficulty_name):
    """
    Draws the top scoreboard area.
    """
    pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))

    draw_text(
        f"SCORE: {score}",
        font_small,
        WHITE,
        20,
        18,
        center=False
    )

    draw_text(
        f"HIGH SCORE: {high_score}",
        font_small,
        YELLOW,
        SCREEN_WIDTH // 2,
        30
    )

    draw_text(
        f"MODE: {difficulty_name}",
        font_small,
        BLUE,
        SCREEN_WIDTH - 170,
        18,
        center=False
    )


def draw_grid():
    """
    Draws a retro grid behind the snake.
    """
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(
            screen,
            DARK_GREEN,
            (x, HEADER_HEIGHT),
            (x, SCREEN_HEIGHT)
        )

    for y in range(HEADER_HEIGHT, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(
            screen,
            DARK_GREEN,
            (0, y),
            (SCREEN_WIDTH, y)
        )


def draw_snake(snake):
    """
    Draws the snake.
    The first segment is the head.
    """
    for index, segment in enumerate(snake):
        x, y = segment

        rect = pygame.Rect(
            x * CELL_SIZE,
            y * CELL_SIZE + HEADER_HEIGHT,
            CELL_SIZE,
            CELL_SIZE
        )

        if index == 0:
            pygame.draw.rect(screen, LIGHT_GREEN, rect)
        else:
            pygame.draw.rect(screen, GREEN, rect)

        pygame.draw.rect(screen, BLACK, rect, 2)


def draw_food(food):
    """
    Draws the food.
    """
    x, y = food

    rect = pygame.Rect(
        x * CELL_SIZE,
        y * CELL_SIZE + HEADER_HEIGHT,
        CELL_SIZE,
        CELL_SIZE
    )

    pygame.draw.rect(screen, RED, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)


def draw_game_screen(snake, food, score, high_score, difficulty_name):
    """
    Draws the full game screen.
    """
    screen.fill(BLACK)

    draw_header(score, high_score, difficulty_name)
    draw_grid()
    draw_food(food)
    draw_snake(snake)

    pygame.display.update()


# -----------------------------
# Game Logic Functions
# -----------------------------

def create_starting_snake():
    """
    Creates the starting snake in the middle of the board.
    """
    center_x = GRID_WIDTH // 2
    center_y = GRID_HEIGHT // 2

    return [
        (center_x, center_y),
        (center_x - 1, center_y),
        (center_x - 2, center_y)
    ]


def create_food(snake):
    """
    Creates food in a random location that is not inside the snake.
    """
    while True:
        food = (
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        )

        if food not in snake:
            return food


def get_new_head(snake, direction):
    """
    Calculates where the snake head should move next.
    """
    head_x, head_y = snake[0]

    if direction == "UP":
        head_y -= 1
    elif direction == "DOWN":
        head_y += 1
    elif direction == "LEFT":
        head_x -= 1
    elif direction == "RIGHT":
        head_x += 1

    return head_x, head_y


def is_wall_collision(position):
    """
    Checks if the snake head hit the wall.
    """
    x, y = position

    if x < 0 or x >= GRID_WIDTH:
        return True

    if y < 0 or y >= GRID_HEIGHT:
        return True

    return False


def is_self_collision(snake):
    """
    Checks if the snake head hit its own body.
    """
    head = snake[0]
    body = snake[1:]

    return head in body


def is_opposite_direction(current_direction, new_direction):
    """
    Prevents the snake from instantly reversing into itself.
    """
    if current_direction == "UP" and new_direction == "DOWN":
        return True

    if current_direction == "DOWN" and new_direction == "UP":
        return True

    if current_direction == "LEFT" and new_direction == "RIGHT":
        return True

    if current_direction == "RIGHT" and new_direction == "LEFT":
        return True

    return False


def update_snake(snake, direction, food):
    """
    Moves the snake and checks whether food was eaten.

    Returns:
        ate_food: True if the snake ate food, otherwise False.
    """
    new_head = get_new_head(snake, direction)

    snake.insert(0, new_head)

    if new_head == food:
        return True

    snake.pop()
    return False


def update_high_score(score, high_score):
    """
    Updates the high score if the current score is higher.
    """
    if score > high_score:
        save_high_score(score)
        return score

    return high_score


# -----------------------------
# Input Handling
# -----------------------------

def handle_quit_event(event):
    """
    Quits the game safely.
    """
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()


def get_direction_from_key(key):
    """
    Converts keyboard input into a movement direction.
    Supports both arrow keys and WASD.
    """
    if key in [pygame.K_UP, pygame.K_w]:
        return "UP"

    if key in [pygame.K_DOWN, pygame.K_s]:
        return "DOWN"

    if key in [pygame.K_LEFT, pygame.K_a]:
        return "LEFT"

    if key in [pygame.K_RIGHT, pygame.K_d]:
        return "RIGHT"

    return None


# -----------------------------
# Menu Screens
# -----------------------------

def start_screen():
    """
    Displays the start menu and lets the player select difficulty.
    """
    selected_speed = MEDIUM_SPEED
    difficulty_name = "MEDIUM"

    while True:
        screen.fill(BLACK)

        draw_text(
            "RETRO SNAKE",
            font_large,
            GREEN,
            SCREEN_WIDTH // 2,
            135
        )

        draw_text(
            "Press ENTER to Start",
            font_medium,
            WHITE,
            SCREEN_WIDTH // 2,
            240
        )

        draw_text(
            "1 = Easy   2 = Medium   3 = Hard",
            font_small,
            YELLOW,
            SCREEN_WIDTH // 2,
            310
        )

        draw_text(
            f"Selected Difficulty: {difficulty_name}",
            font_small,
            BLUE,
            SCREEN_WIDTH // 2,
            360
        )

        draw_text(
            "Move with Arrow Keys or WASD",
            font_small,
            GRAY,
            SCREEN_WIDTH // 2,
            440
        )

        draw_text(
            "P = Pause    ESC = Quit",
            font_small,
            GRAY,
            SCREEN_WIDTH // 2,
            480
        )

        pygame.display.update()

        for event in pygame.event.get():
            handle_quit_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_1:
                    selected_speed = EASY_SPEED
                    difficulty_name = "EASY"

                elif event.key == pygame.K_2:
                    selected_speed = MEDIUM_SPEED
                    difficulty_name = "MEDIUM"

                elif event.key == pygame.K_3:
                    selected_speed = HARD_SPEED
                    difficulty_name = "HARD"

                elif event.key == pygame.K_RETURN:
                    return selected_speed, difficulty_name


def pause_screen():
    """
    Displays pause text.
    """
    draw_text(
        "PAUSED",
        font_large,
        YELLOW,
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 - 30
    )

    draw_text(
        "Press P to Resume",
        font_small,
        WHITE,
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 + 35
    )

    pygame.display.update()


def game_over_screen(score, high_score):
    """
    Displays the game over screen.
    """
    while True:
        screen.fill(BLACK)

        draw_text(
            "GAME OVER",
            font_large,
            RED,
            SCREEN_WIDTH // 2,
            150
        )

        draw_text(
            f"Final Score: {score}",
            font_medium,
            WHITE,
            SCREEN_WIDTH // 2,
            260
        )

        draw_text(
            f"High Score: {high_score}",
            font_medium,
            YELLOW,
            SCREEN_WIDTH // 2,
            315
        )

        draw_text(
            "Press ENTER to Play Again",
            font_small,
            WHITE,
            SCREEN_WIDTH // 2,
            420
        )

        draw_text(
            "Press ESC to Quit",
            font_small,
            GRAY,
            SCREEN_WIDTH // 2,
            465
        )

        pygame.display.update()

        for event in pygame.event.get():
            handle_quit_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# -----------------------------
# Main Gameplay
# -----------------------------

def play_game(speed, difficulty_name):
    """
    Runs one round of the Snake game.
    """
    snake = create_starting_snake()
    food = create_food(snake)

    direction = "RIGHT"
    next_direction = "RIGHT"

    score = 0
    high_score = load_high_score()

    paused = False

    while True:
        clock.tick(speed)

        for event in pygame.event.get():
            handle_quit_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_p:
                    paused = not paused

                new_direction = get_direction_from_key(event.key)

                if new_direction is not None:
                    if not is_opposite_direction(direction, new_direction):
                        next_direction = new_direction

        if paused:
            draw_game_screen(
                snake,
                food,
                score,
                high_score,
                difficulty_name
            )
            pause_screen()
            continue

        direction = next_direction

        ate_food = update_snake(snake, direction, food)

        if is_wall_collision(snake[0]) or is_self_collision(snake):
            high_score = update_high_score(score, high_score)
            return score, high_score

        if ate_food:
            score += 1
            high_score = update_high_score(score, high_score)
            food = create_food(snake)

        draw_game_screen(
            snake,
            food,
            score,
            high_score,
            difficulty_name
        )


def main():
    """
    Main program loop.
    """
    while True:
        speed, difficulty_name = start_screen()
        score, high_score = play_game(speed, difficulty_name)
        game_over_screen(score, high_score)


if __name__ == "__main__":
    main()