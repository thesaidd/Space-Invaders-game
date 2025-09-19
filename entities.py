from __future__ import annotations
import pygame
from dataclasses import dataclass
from typing import List, Optional
import random
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PLAYER_SPEED,
    PLAYER_SHOOT_COOLDOWN_MS,
    BULLET_SPEED,
    ENEMY_BULLET_SPEED,
    ENEMY_COLS,
    ENEMY_ROWS,
    ENEMY_X_PADDING,
    ENEMY_Y_PADDING,
    ENEMY_START_Y,
    ENEMY_HMOVE_PIXELS,
    ENEMY_VMOVE_PIXELS,
    ENEMY_MOVE_INTERVAL_MS,
    ENEMY_SHOOT_CHANCE,
)


@dataclass
class Bullet:
    rect: pygame.Rect
    vy: int
    from_player: bool
    alive: bool = True

    def update(self) -> None:
        self.rect.y += self.vy
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.alive = False


class Player:
    def __init__(self, image: pygame.Surface, shoot_sound) -> None:
        self.image = image
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        self.cooldown_ms = PLAYER_SHOOT_COOLDOWN_MS
        self.last_shot_time = 0
        self.shoot_sound = shoot_sound
        self.alive = True

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def try_shoot(self, bullets: List[Bullet], now_ms: int, bullet_image: pygame.Surface) -> None:
        if now_ms - self.last_shot_time < self.cooldown_ms or not self.alive:
            return
        self.last_shot_time = now_ms
        bullet_rect = bullet_image.get_rect(midbottom=self.rect.midtop)
        bullets.append(Bullet(bullet_rect, BULLET_SPEED, True))
        if self.shoot_sound:
            self.shoot_sound.play()


class Enemy:
    def __init__(self, image: pygame.Surface, x: int, y: int) -> None:
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.alive = True


class EnemyFormation:
    def __init__(self, enemy_image: pygame.Surface, enemy_bullet_image: pygame.Surface, hit_sound, shoot_chance: float = ENEMY_SHOOT_CHANCE) -> None:
        self.enemy_image = enemy_image
        self.enemy_bullet_image = enemy_bullet_image
        self.hit_sound = hit_sound
        self.shoot_chance = shoot_chance
        self.enemies: List[Enemy] = []
        self.direction = 1  # 1 right, -1 left
        self.last_move_time = 0
        self.move_interval_ms = ENEMY_MOVE_INTERVAL_MS
        self._spawn_grid()

    def _spawn_grid(self) -> None:
        self.enemies.clear()
        for row in range(ENEMY_ROWS):
            for col in range(ENEMY_COLS):
                x = ENEMY_X_PADDING + col * ENEMY_X_PADDING
                y = ENEMY_START_Y + row * ENEMY_Y_PADDING
                self.enemies.append(Enemy(self.enemy_image, x, y))

    def update(self, now_ms: int, bullets: List[Bullet]) -> None:
        if now_ms - self.last_move_time >= self.move_interval_ms:
            self.last_move_time = now_ms
            # Horizontal move and boundary check
            min_x = min((e.rect.left for e in self.enemies if e.alive), default=0)
            max_x = max((e.rect.right for e in self.enemies if e.alive), default=0)
            if max_x == 0:  # all dead
                return
            if (self.direction > 0 and max_x + ENEMY_HMOVE_PIXELS >= SCREEN_WIDTH - 10) or (
                self.direction < 0 and min_x - ENEMY_HMOVE_PIXELS <= 10
            ):
                # Move down and reverse
                for e in self.enemies:
                    if e.alive:
                        e.rect.y += ENEMY_VMOVE_PIXELS
                self.direction *= -1
            else:
                for e in self.enemies:
                    if e.alive:
                        e.rect.x += ENEMY_HMOVE_PIXELS * self.direction

        # Random shooting from bottom-most enemies per column
        columns = {}
        for e in self.enemies:
            if e.alive:
                col = e.rect.x // ENEMY_X_PADDING
                if col not in columns or e.rect.y > columns[col].rect.y:
                    columns[col] = e
        for e in columns.values():
            if random.random() < self.shoot_chance:
                rect = self.enemy_bullet_image.get_rect(midtop=e.rect.midbottom)
                bullets.append(Bullet(rect, ENEMY_BULLET_SPEED, False))

    def check_collision_with_bullets(self, bullets: List[Bullet]) -> int:
        score = 0
        for e in self.enemies:
            if not e.alive:
                continue
            for b in bullets:
                if b.alive and b.from_player and e.rect.colliderect(b.rect):
                    e.alive = False
                    b.alive = False
                    score += 100
                    if self.hit_sound:
                        self.hit_sound.play()
                    break
        return score

    def any_reached_bottom(self) -> bool:
        return any(e.alive and e.rect.bottom >= SCREEN_HEIGHT - 60 for e in self.enemies)

    def all_dead(self) -> bool:
        return all(not e.alive for e in self.enemies)


