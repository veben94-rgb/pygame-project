import pygame
import random
import sqlite3

pygame.init()

WIDTH = 800
HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Практика")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 22)


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("scores.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                score INTEGER
            )
        ''')
        self.conn.commit()

    def add_score(self, name, score):
        self.cursor.execute(
            "INSERT INTO scores (name, score) VALUES (?, ?)",
            (name, score)
        )
        self.conn.commit()

    def get_top_scores(self):
        self.cursor.execute(
            "SELECT name, score FROM scores ORDER BY score DESC LIMIT 5"
        )
        return self.cursor.fetchall()


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.speed = 5
        self.score = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed

        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed

        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed

        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.width, self.height))


class Enemy:
    def __init__(self):
        self.size = 40
        self.x = random.randint(0, WIDTH - self.size)
        self.y = random.randint(-300, -40)
        self.speed = random.randint(4, 8)

    def move(self):
        self.y += self.speed

        if self.y > HEIGHT:
            self.y = random.randint(-300, -40)
            self.x = random.randint(0, WIDTH - self.size)
            self.speed = random.randint(4, 8)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, (self.x, self.y, self.size, self.size))

    def collide(self, player):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        enemy_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        return player_rect.colliderect(enemy_rect)


class Coin:
    def __init__(self):
        self.size = 25
        self.respawn()

    def respawn(self):
        self.x = random.randint(0, WIDTH - self.size)
        self.y = random.randint(0, HEIGHT - self.size)

    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, (self.x, self.y), self.size)

    def collect(self, player):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        coin_rect = pygame.Rect(self.x, self.y, self.size, self.size)

        if player_rect.colliderect(coin_rect):
            self.respawn()
            return True

        return False


# Ввод имени игрока
player_name = ""
input_active = True

while input_active:
    screen.fill(WHITE)

    title = font.render("Введите ваше имя:", True, BLACK)
    name_text = font.render(player_name, True, BLUE)

    screen.blit(title, (250, 220))
    screen.blit(name_text, (250, 280))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if player_name.strip() != "":
                    input_active = False

            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]

            else:
                if len(player_name) < 12:
                    player_name += event.unicode


player = Player(WIDTH // 2, HEIGHT - 100)
enemies = [Enemy() for _ in range(5)]
coin = Coin()
db = Database()

running = True
game_over = False
win = False

TARGET_SCORE = 25

score_saved = False

while running:
    clock.tick(FPS)

    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                
                player_name = ""
                input_active = True

                while input_active:
                    screen.fill(WHITE)

                    title = font.render(
                        "Введите ваше имя:",
                        True,
                        BLACK
                    )

                    name_text = font.render(
                        player_name,
                        True,
                        BLUE
                    )

                    screen.blit(title, (250, 220))
                    screen.blit(name_text, (250, 280))

                    pygame.display.update()

                    for input_event in pygame.event.get():

                        if input_event.type == pygame.QUIT:
                            pygame.quit()
                            exit()

                        if input_event.type == pygame.KEYDOWN:

                            if input_event.key == pygame.K_RETURN:
                                if player_name.strip() != "":
                                    input_active = False

                            elif input_event.key == pygame.K_BACKSPACE:
                                player_name = player_name[:-1]

                            else:
                                if len(player_name) < 12:
                                    player_name += input_event.unicode

                player = Player(WIDTH // 2, HEIGHT - 100)
                enemies = [Enemy() for _ in range(5)]
                coin = Coin()

                game_over = False
                win = False
                score_saved = False

    if not game_over:
        keys = pygame.key.get_pressed()
        player.move(keys)

        for enemy in enemies:
            enemy.move()

            if enemy.collide(player):
                game_over = True

        if coin.collect(player):
            player.score += 1

        if player.score >= TARGET_SCORE:
            win = True
            game_over = True

        player.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        coin.draw(screen)

        score_text = font.render(
            f"Очки: {player.score}",
            True,
            BLACK
        )

        screen.blit(score_text, (20, 20))

        info_text = small_font.render(
            "Соберите 26 монет и избегайте красных врагов.Передвигайтесь стрелочками",
            True,
            BLACK
        )
        screen.blit(info_text, (20, 60))

    else:
        if not score_saved:
            db.add_score(player_name, player.score)
            score_saved = True

        if win:
            result_text = font.render("ПОБЕДА!", True, GREEN)
        else:
            result_text = font.render("ПОРАЖЕНИЕ!", True, RED)

        screen.blit(result_text, (300, 120))

        top_scores = db.get_top_scores()

        y = 250

        for i, (name, score) in enumerate(top_scores, start=1):
            line = small_font.render(
                f"{i}. {name} - {score}",
                True,
                BLACK
            )

            screen.blit(line, (280, y))
            y += 40

        restart_text = small_font.render(
            "Нажмите R для рестарта",
            True,
            BLACK
        )

        screen.blit(restart_text, (230, 500))

    pygame.display.update()

pygame.quit()
