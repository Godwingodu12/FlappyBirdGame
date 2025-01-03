import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Define screen dimensions
WIDTH = 1270
HEIGHT = 720

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Flappy Bird Test")

# Initialize the clock
CLOCK = pygame.time.Clock()

# Load and scale images
def load_and_scale_image(path, width, height):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, (width, height))

# Load images
BACKGROUND = load_and_scale_image("background.png", WIDTH, HEIGHT)
BIRD = load_and_scale_image("bird.png", 50, 35)
PIPE = load_and_scale_image("pipe.png", 100, 500)
ROTATED_PIPE = load_and_scale_image("rotated_pipe.png", 100, 500)
GROUND = load_and_scale_image("ground.png", WIDTH, 100)
SCORE_BOOST = load_and_scale_image("sfx_boost.png", 50, 50)

# Load sounds
def load_sound(path):
    sound = pygame.mixer.Sound(path)
    sound.set_volume(0.3)  # Adjust volume for all sounds
    return sound

POINT_SOUND = load_sound("sfx_point.wav")
HIT_SOUND = load_sound("sfx_hit.wav")
BOOST_SOUND = load_sound("sfx_boost.wav")

# File path for high score
HIGH_SCORE_FILE = "highscore.txt"

# Pipe gap
PIPE_GAP = 350  # Increased gap for easier navigation

class Pipe:
    def __init__(self, x, gap):
        self.x = x
        self.gap = gap
        self.height = random.randint(100, 400)
        self.y = HEIGHT - GROUND.get_height() - self.height

    def move(self):
        self.x -= 5  # Pipe velocity

    def off_screen(self):
        return self.x < -PIPE.get_width()

    def draw(self):
        screen.blit(PIPE, (self.x, self.y))
        screen.blit(ROTATED_PIPE, (self.x, self.y - self.gap - (HEIGHT - GROUND.get_height() - self.height)))

class ScoreBoost:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.x -= 5  # Boost velocity

    def off_screen(self):
        return self.x < -SCORE_BOOST.get_width()

    def draw(self):
        screen.blit(SCORE_BOOST, (self.x, self.y))

class Game:
    def __init__(self):
        self.high_score = self.load_high_score()
        self.reset_game()

    def load_high_score(self):
        if os.path.isfile(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as file:
                return int(file.read().strip())
        return 0

    def save_high_score(self):
        with open(HIGH_SCORE_FILE, 'w') as file:
            file.write(str(self.high_score))

    def reset_game(self):
        self.game_on = True
        self.bird_x = 100
        self.bird_y = HEIGHT // 2
        self.pipes = []
        self.boosts = []
        self.gravity = 0
        self.flap = 0
        self.score = 0
        self.bird_rot_angle = 0
        self.is_game_over = False
        self.pipe_passed = []
        self.pipe_timer = 0
        self.has_played_hit_sound = False  # Flag for hit sound
        self.boost_active = False  # Boost active status
        self.boost_timer = 0  # Timer for the boost effect duration

    def spawn_pipe(self):
        new_pipe = Pipe(WIDTH + PIPE.get_width(), PIPE_GAP)
        self.pipes.append(new_pipe)
        self.pipe_passed.append(False)

    def spawn_boost(self, last_pipe):
        # Randomly decide whether to spawn a boost (25% chance)
        if random.random() < 0.25:  # 25% spawn rate
            if last_pipe:
                boost_x = last_pipe.x + last_pipe.height + 50  # Ensure boost is after the last pipe
                boost_y = random.randint(50, last_pipe.y - 50)  # Ensure boost doesn't overlap with ground
                new_boost = ScoreBoost(boost_x, boost_y)
                self.boosts.append(new_boost)

    def flapping(self):
        self.gravity += 0.8  # Increased gravity for faster fall
        self.bird_y += self.gravity
        if self.flap > 0:
            self.flap -= 1
            self.bird_y -= 8  # Reduced flap strength for less upward movement
            self.bird_rot_angle = -30
        else:
            self.bird_rot_angle = min(self.bird_rot_angle + 2, 90)

    def update_score(self):
        bird_rect = pygame.Rect(self.bird_x, self.bird_y, BIRD.get_width(), BIRD.get_height())
        for index, pipe in enumerate(self.pipes):
            if pipe.x + PIPE.get_width() < self.bird_x and not self.pipe_passed[index]:
                self.score += 1
                self.pipe_passed[index] = True
                pygame.mixer.Sound.play(POINT_SOUND)

        for boost in self.boosts:
            if bird_rect.colliderect(pygame.Rect(boost.x, boost.y, SCORE_BOOST.get_width(), SCORE_BOOST.get_height())):
                self.boosts.remove(boost)
                self.boost_active = True  # Activate boost
                self.boost_timer = 300  # Set boost duration (in frames)
                pygame.mixer.Sound.play(BOOST_SOUND)

    def is_collide(self):
        bird_rect = pygame.Rect(self.bird_x, self.bird_y, BIRD.get_width(), BIRD.get_height())
        for pipe in self.pipes:
            pipe_rect = pygame.Rect(pipe.x, pipe.y, PIPE.get_width(), pipe.height)
            top_pipe_rect = pygame.Rect(pipe.x, pipe.y - pipe.gap - (HEIGHT - GROUND.get_height() - pipe.height), PIPE.get_width(), (HEIGHT - GROUND.get_height() - pipe.height))
            if bird_rect.colliderect(pipe_rect) or bird_rect.colliderect(top_pipe_rect):
                return True

        # Ground collision
        if self.bird_y + BIRD.get_height() >= HEIGHT - GROUND.get_height():
            return True

        return False

    def game_over(self):
        if self.is_collide() and not self.boost_active:  # Only collide if boost is not active
            if not self.is_game_over:  # Play sound only once
                pygame.mixer.Sound.play(HIT_SOUND)
                self.has_played_hit_sound = True
            self.is_game_over = True
            
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
                
            # Display Game Over and Score
            self.display_text(f"Score: {self.score}", (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 100, 68, "Fixedsys", bold=True)
            self.display_text(f"High Score: {self.high_score}", (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 40, 48, "Fixedsys", bold=True)
            self.display_text("Game Over!", (255, 255, 255), WIDTH // 2, HEIGHT // 2 - 200, 84, "Fixedsys", bold=True)
            self.display_text("Press Enter To Play Again", (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 20, 48, "Fixedsys", bold=True)
            self.display_text("Press ESC to Exit", (255, 255, 255), WIDTH // 2, HEIGHT // 2 + 80, 48, "Fixedsys", bold=True)

    def display_text(self, text, color, x, y, size, font_name, bold=False):
        font = pygame.font.SysFont(font_name, size, bold=bold)
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x - text_surface.get_width() // 2, y))

    def main_game(self):
        while True:
            screen.blit(BACKGROUND, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.flap = 10  # Adjust flap power if necessary
                        self.gravity = -6  # Reduced gravity effect when flapping
                    if self.is_game_over and event.key == pygame.K_RETURN:
                        self.reset_game()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            if not self.is_game_over:
                self.flapping()
                self.update_score()

                # Spawn a new pipe every 150 frames (adjust as necessary for difficulty)
                if self.pipe_timer % 150 == 0:
                    self.spawn_pipe()
                    if self.pipes:
                        self.spawn_boost(self.pipes[-1])  # Spawn boost relative to the last pipe

                # Move and draw pipes
                for pipe in self.pipes:
                    pipe.move()
                    pipe.draw()

                # Move and draw boosts
                for boost in self.boosts:
                    boost.move()
                    boost.draw()

                # Remove off-screen pipes and boosts
                self.pipes = [pipe for pipe in self.pipes if not pipe.off_screen()]
                self.boosts = [boost for boost in self.boosts if not boost.off_screen()]

                # Check for boost timer
                if self.boost_active:
                    self.boost_timer -= 1
                    if self.boost_timer <= 0:
                        self.boost_active = False  # Deactivate boost when timer runs out

                # Draw the bird
                rotated_bird = pygame.transform.rotate(BIRD, self.bird_rot_angle)
                screen.blit(rotated_bird, (self.bird_x, self.bird_y))

                # Draw ground
                screen.blit(GROUND, (0, HEIGHT - GROUND.get_height()))

                # Display score
                self.display_text(str(self.score), (255, 255, 255), WIDTH // 2, 50, 48, "Fixedsys", bold=True)

                # Display boost timer if boost is active
                if self.boost_active:
                    seconds_left = self.boost_timer // 60  # Convert frames to seconds
                    self.display_text(f"Boost Time: {seconds_left}s", (255, 255, 255), WIDTH - 150, 50, 32, "Fixedsys")

                # Check game over status
                self.game_over()

                # Increment pipe timer
                self.pipe_timer += 1

            # Refresh screen
            pygame.display.update()
            CLOCK.tick(60)

# Run the game
game = Game()
game.main_game()
