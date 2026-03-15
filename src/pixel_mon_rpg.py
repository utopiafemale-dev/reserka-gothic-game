"""PixelMon RPG - a tiny Pokémon-inspired 2D pixel RPG prototype.

Run:
    python src/pixel_mon_rpg.py

Optional smoke test:
    SDL_VIDEODRIVER=dummy python src/pixel_mon_rpg.py --autotest
"""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass

import pygame

TILE_SIZE = 32
MAP_W = 20
MAP_H = 15
SCREEN_W = MAP_W * TILE_SIZE
SCREEN_H = MAP_H * TILE_SIZE
FPS = 60

# Palette
BLACK = (25, 25, 25)
WHITE = (240, 240, 240)
GRASS = (88, 170, 78)
TALL_GRASS = (62, 132, 58)
WATER = (68, 122, 214)
PATH = (170, 148, 106)
TREE = (36, 95, 34)
HOUSE = (186, 94, 84)
ROOF = (123, 52, 46)
UI_BG = (30, 30, 40)
UI_ALT = (46, 46, 64)
HP_GREEN = (85, 206, 100)
HP_RED = (198, 69, 69)


@dataclass
class Monster:
    name: str
    max_hp: int
    hp: int
    attack: int
    defense: int


class PixelMonRPG:
    def __init__(self, autotest: bool = False):
        pygame.init()
        pygame.display.set_caption("PixelMon RPG")
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.small_font = pygame.font.SysFont("consolas", 16)

        self.autotest = autotest
        self.frame_count = 0

        self.map_data = self.build_map()
        self.player_x = 2
        self.player_y = 11
        self.facing = "down"

        self.state = "overworld"  # overworld | battle | dialogue
        self.message = "Explore the town and walk through tall grass for encounters!"

        self.hero = Monster("Leafcub", 36, 36, 11, 6)
        self.enemy = None
        self.selected_action = 0
        self.dialogue_timer = 0

        self.healer_pos = (4, 3)
        self.sign_pos = (10, 2)

    def build_map(self):
        world = [["G" for _ in range(MAP_W)] for _ in range(MAP_H)]

        # Border trees
        for x in range(MAP_W):
            world[0][x] = "T"
            world[MAP_H - 1][x] = "T"
        for y in range(MAP_H):
            world[y][0] = "T"
            world[y][MAP_W - 1] = "T"

        # Water pond
        for y in range(8, 12):
            for x in range(13, 18):
                world[y][x] = "W"

        # Tall grass patch
        for y in range(4, 9):
            for x in range(7, 12):
                world[y][x] = "g"

        # Main path
        for x in range(2, 16):
            world[11][x] = "P"
        for y in range(3, 12):
            world[y][4] = "P"

        # House tiles
        for y in range(2, 5):
            for x in range(2, 6):
                world[y][x] = "H"
        for x in range(2, 6):
            world[1][x] = "R"

        return world

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

            if self.autotest:
                self.frame_count += 1
                if self.frame_count > 30:
                    break

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

                if self.state == "overworld":
                    self.handle_overworld_input(event.key)
                elif self.state == "battle":
                    self.handle_battle_input(event.key)

    def handle_overworld_input(self, key):
        dx, dy = 0, 0
        if key in (pygame.K_UP, pygame.K_w):
            dy, self.facing = -1, "up"
        elif key in (pygame.K_DOWN, pygame.K_s):
            dy, self.facing = 1, "down"
        elif key in (pygame.K_LEFT, pygame.K_a):
            dx, self.facing = -1, "left"
        elif key in (pygame.K_RIGHT, pygame.K_d):
            dx, self.facing = 1, "right"
        elif key == pygame.K_e:
            self.try_interact()
            return

        if dx or dy:
            nx, ny = self.player_x + dx, self.player_y + dy
            if self.is_walkable(nx, ny):
                self.player_x, self.player_y = nx, ny
                self.try_encounter()

    def handle_battle_input(self, key):
        actions = ["Attack", "Skill", "Item", "Run"]
        if key in (pygame.K_UP, pygame.K_w):
            self.selected_action = (self.selected_action - 1) % len(actions)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected_action = (self.selected_action + 1) % len(actions)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            self.resolve_player_turn(actions[self.selected_action])

    def try_interact(self):
        tx, ty = self.player_x, self.player_y
        if self.facing == "up":
            ty -= 1
        elif self.facing == "down":
            ty += 1
        elif self.facing == "left":
            tx -= 1
        elif self.facing == "right":
            tx += 1

        if (tx, ty) == self.healer_pos:
            self.hero.hp = self.hero.max_hp
            self.message = "Healer: Your PixelMon are fully restored!"
            self.dialogue_timer = FPS * 3
        elif (tx, ty) == self.sign_pos:
            self.message = "Sign: Tip - Tall grass hides wild PixelMon."
            self.dialogue_timer = FPS * 3

    def is_walkable(self, x, y):
        if x < 0 or x >= MAP_W or y < 0 or y >= MAP_H:
            return False
        tile = self.map_data[y][x]
        return tile in {"G", "g", "P"}

    def try_encounter(self):
        tile = self.map_data[self.player_y][self.player_x]
        if tile == "g" and random.random() < 0.15:
            monsters = [
                Monster("Sproutle", 26, 26, 8, 4),
                Monster("Bubbloon", 30, 30, 7, 5),
                Monster("Embermoth", 24, 24, 10, 3),
            ]
            self.enemy = random.choice(monsters)
            self.state = "battle"
            self.selected_action = 0
            self.message = f"A wild {self.enemy.name} appeared!"

    def damage_roll(self, attacker: Monster, defender: Monster, bonus=0):
        base = attacker.attack + bonus - defender.defense // 2
        return max(1, base + random.randint(-2, 3))

    def resolve_player_turn(self, action):
        if not self.enemy:
            return

        if action == "Attack":
            dmg = self.damage_roll(self.hero, self.enemy)
            self.enemy.hp -= dmg
            self.message = f"{self.hero.name} used Tackle! {dmg} damage."
        elif action == "Skill":
            dmg = self.damage_roll(self.hero, self.enemy, bonus=4)
            self.enemy.hp -= dmg
            self.message = f"{self.hero.name} cast Leaf Burst! {dmg} damage."
        elif action == "Item":
            heal = 10
            self.hero.hp = min(self.hero.max_hp, self.hero.hp + heal)
            self.message = f"You used a Potion. {self.hero.name} healed {heal} HP."
        elif action == "Run":
            if random.random() < 0.55:
                self.state = "overworld"
                self.message = "Got away safely!"
                self.enemy = None
                return
            self.message = "Couldn't escape!"

        if self.enemy and self.enemy.hp <= 0:
            self.state = "overworld"
            self.message = f"{self.enemy.name} fainted! You earned 20 XP."
            self.enemy = None
            return

        self.enemy_turn()

    def enemy_turn(self):
        if not self.enemy:
            return
        dmg = self.damage_roll(self.enemy, self.hero)
        self.hero.hp -= dmg
        self.message += f"  {self.enemy.name} hit back for {dmg}!"
        if self.hero.hp <= 0:
            self.hero.hp = self.hero.max_hp
            self.state = "overworld"
            self.player_x, self.player_y = 4, 4
            self.message = "You blacked out and woke up at the healer's house."
            self.enemy = None

    def update(self):
        if self.dialogue_timer > 0:
            self.dialogue_timer -= 1
            if self.dialogue_timer == 0 and self.state == "overworld":
                self.message = "Explore the town and walk through tall grass for encounters!"

    def draw(self):
        if self.state == "overworld":
            self.draw_overworld()
        else:
            self.draw_battle()

        self.draw_message_bar()

    def draw_overworld(self):
        self.screen.fill(BLACK)
        for y in range(MAP_H):
            for x in range(MAP_W):
                tile = self.map_data[y][x]
                color = GRASS
                if tile == "g":
                    color = TALL_GRASS
                elif tile == "W":
                    color = WATER
                elif tile == "P":
                    color = PATH
                elif tile == "T":
                    color = TREE
                elif tile == "H":
                    color = HOUSE
                elif tile == "R":
                    color = ROOF

                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

        hx, hy = self.healer_pos
        pygame.draw.rect(
            self.screen,
            (255, 230, 230),
            pygame.Rect(hx * TILE_SIZE + 8, hy * TILE_SIZE + 8, 16, 16),
        )

        sx, sy = self.sign_pos
        pygame.draw.rect(
            self.screen,
            (240, 210, 120),
            pygame.Rect(sx * TILE_SIZE + 9, sy * TILE_SIZE + 6, 14, 18),
        )

        px = self.player_x * TILE_SIZE
        py = self.player_y * TILE_SIZE
        pygame.draw.rect(self.screen, (235, 235, 255), pygame.Rect(px + 8, py + 6, 16, 20))
        pygame.draw.rect(self.screen, (65, 86, 165), pygame.Rect(px + 8, py + 20, 16, 6))

        hp_text = self.small_font.render(
            f"{self.hero.name} HP: {max(0, self.hero.hp)}/{self.hero.max_hp}", True, WHITE
        )
        self.screen.blit(hp_text, (8, 8))

    def draw_hp_bar(self, x, y, width, hp, max_hp):
        pygame.draw.rect(self.screen, UI_ALT, pygame.Rect(x, y, width, 10))
        ratio = max(0, hp) / max_hp
        fill_color = HP_GREEN if ratio > 0.35 else HP_RED
        pygame.draw.rect(self.screen, fill_color, pygame.Rect(x, y, int(width * ratio), 10))
        pygame.draw.rect(self.screen, WHITE, pygame.Rect(x, y, width, 10), 1)

    def draw_battle(self):
        self.screen.fill((96, 171, 103))
        pygame.draw.ellipse(self.screen, (75, 145, 85), pygame.Rect(70, 300, 240, 80))
        pygame.draw.ellipse(self.screen, (75, 145, 85), pygame.Rect(360, 130, 220, 70))

        pygame.draw.rect(self.screen, (180, 220, 120), pygame.Rect(430, 135, 44, 44))
        pygame.draw.rect(self.screen, (220, 245, 160), pygame.Rect(120, 280, 58, 58))

        pygame.draw.rect(self.screen, UI_BG, pygame.Rect(20, 24, 260, 72), border_radius=8)
        pygame.draw.rect(self.screen, UI_BG, pygame.Rect(360, 324, 260, 72), border_radius=8)

        hero_name = self.small_font.render(self.hero.name, True, WHITE)
        self.screen.blit(hero_name, (32, 32))
        self.draw_hp_bar(32, 58, 180, self.hero.hp, self.hero.max_hp)

        if self.enemy:
            enemy_name = self.small_font.render(self.enemy.name, True, WHITE)
            self.screen.blit(enemy_name, (372, 332))
            self.draw_hp_bar(372, 358, 180, self.enemy.hp, self.enemy.max_hp)

        actions = ["Attack", "Skill", "Item", "Run"]
        pygame.draw.rect(self.screen, UI_BG, pygame.Rect(20, 412, 600, 120), border_radius=8)
        for i, action in enumerate(actions):
            color = (255, 214, 108) if i == self.selected_action else WHITE
            txt = self.font.render(action, True, color)
            self.screen.blit(txt, (42, 430 + i * 24))

    def draw_message_bar(self):
        pygame.draw.rect(self.screen, UI_BG, pygame.Rect(0, SCREEN_H - 54, SCREEN_W, 54))
        pygame.draw.line(self.screen, UI_ALT, (0, SCREEN_H - 54), (SCREEN_W, SCREEN_H - 54), 2)
        msg = self.small_font.render(self.message[:90], True, WHITE)
        self.screen.blit(msg, (12, SCREEN_H - 36))


def main():
    parser = argparse.ArgumentParser(description="Pokémon-inspired pixel RPG prototype")
    parser.add_argument(
        "--autotest",
        action="store_true",
        help="Run briefly and exit (useful for CI/headless validation).",
    )
    args = parser.parse_args()

    game = PixelMonRPG(autotest=args.autotest)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
