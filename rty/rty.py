import pygame
import math
import random

pygame.init()

win = pygame.display.set_mode((1500, 800))
pygame.display.set_caption("Игра со спрайтом!")

background1 = pygame.image.load("pixil-frame-0.png").convert()
background1 = pygame.transform.scale(background1, (1500, 800))

background2 = pygame.image.load("boxing.png").convert()
background2 = pygame.transform.scale(background2, (1500, 800))

background3 = pygame.image.load("fgh.png").convert()
background3 = pygame.transform.scale(background3, (1500, 800))

walk_down = pygame.image.load("down.png").convert_alpha()
walk_up = pygame.image.load("up.png").convert_alpha()
walk_left = pygame.image.load("left.png").convert_alpha()
walk_right = pygame.image.load("right.png").convert_alpha()

monster_image = pygame.image.load("howl.png").convert_alpha()

current_map = 1
current_background = background1

portal_zone = pygame.Rect(1355, 235, 80, 80)
house_zone = pygame.Rect(725, 120, 60, 60)

class Rty:
    def __init__(self, x, y, name, health, armor, power, weapon):
        self.x = x
        self.y = y
        self.base_vel = 5
        self.name = name
        self.health = health
        self.armor = armor
        self.power = power
        self.weapon = weapon
        self.stamina = 100
        self.current_image = walk_down
        self.font = pygame.font.SysFont(None, 24)

    def move(self, keys):
        sprinting = keys[pygame.K_LSHIFT] and self.stamina > 0
        speed = self.base_vel * 1.5 if sprinting else self.base_vel
        moved = False

        if keys[pygame.K_w]:
            self.y -= speed
            self.current_image = walk_up
            moved = True
        if keys[pygame.K_s]:
            self.y += speed
            self.current_image = walk_down
            moved = True
        if keys[pygame.K_a]:
            self.x -= speed
            self.current_image = walk_left
            moved = True
        if keys[pygame.K_d]:
            self.x += speed
            self.current_image = walk_right
            moved = True

        if moved and sprinting:
            self.stamina = max(0, self.stamina - 1)
        elif not sprinting and self.stamina < 100:
            self.stamina = min(100, self.stamina + 0.5)

    def draw(self, window):
        window.blit(self.current_image, (self.x, self.y))
        stamina_text = self.font.render(f"{int(self.stamina)}", True, (255, 255, 0))
        window.blit(stamina_text, (self.x + 10, self.y - 20))

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = (255, 0, 0)
        self.speed = 12
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1
        self.vel_x = (dx / distance) * self.speed
        self.vel_y = (dy / distance) * self.speed

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self, window):
        pygame.draw.circle(window, self.color, (int(self.x), int(self.y)), self.radius)

class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 50
        self.image = monster_image

    def move_towards(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        self.x += (dx / dist) * 2
        self.y += (dy / dist) * 2

    def draw(self, window):
        window.blit(self.image, (self.x, self.y))

monsters = []
spawned = False

clock = pygame.time.Clock()
player = Rty(200, 200, "Рыцарь", 100, 50, 20, "Пульки")
bullets = []

run = True
while run:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            bullet_x = player.x + walk_down.get_width() // 2
            bullet_y = player.y + walk_down.get_height() // 2
            bullets.append(Bullet(bullet_x, bullet_y, mx, my))

    keys = pygame.key.get_pressed()
    player.move(keys)

    player_rect = pygame.Rect(player.x, player.y, walk_down.get_width(), walk_down.get_height())

    if current_map == 1:
        if portal_zone.colliderect(player_rect):
            current_map = 2
            current_background = background2
            player.x, player.y = 200, 200
            spawned = False
        elif house_zone.colliderect(player_rect):
            current_map = 3
            current_background = background3
            player.x, player.y = 200, 200

    if current_map == 2 and not spawned:
        monsters = [Monster(random.randint(100, 1400), random.randint(100, 700)) for _ in range(random.randint(5, 10))]
        spawned = True

    win.blit(current_background, (0, 0))

    if current_map == 1:
        pygame.draw.rect(win, (0, 0, 255), portal_zone, 2)
        pygame.draw.rect(win, (0, 255, 0), house_zone, 2)

    for bullet in bullets[:]:
        bullet.move()
        bullet_rect = pygame.Rect(int(bullet.x), int(bullet.y), bullet.radius*2, bullet.radius*2)
        for monster in monsters[:]:
            monster_rect = pygame.Rect(monster.x, monster.y, monster.image.get_width(), monster.image.get_height())
            if bullet_rect.colliderect(monster_rect):
                monster.health -= 25
                if monster.health <= 0:
                    monsters.remove(monster)
                bullets.remove(bullet)
                break
        bullet.draw(win)

    if current_map == 2:
        for monster in monsters:
            monster.move_towards(player)
            monster.draw(win)
        if not monsters:
            current_map = 1
            current_background = background1
            player.x, player.y = 200, 200

    player.draw(win)
    hp_font = pygame.font.SysFont(None, 36)
    hp_text = hp_font.render(f"HP: {int(player.health)}", True, (255, 0, 0))
    win.blit(hp_text, (20, 20))

    pygame.display.update()

pygame.quit()
