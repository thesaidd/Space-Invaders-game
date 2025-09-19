import pygame
from typing import List
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    COLOR_BG,
    COLOR_WHITE,
    WINDOW_TITLE,
)
from assets_loader import Assets
from entities import Player, Bullet, EnemyFormation
from effects import Explosion


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_large = pygame.font.SysFont("Arial", 40)
        self.font_small = pygame.font.SysFont("Arial", 24)

        self.assets = Assets()
        self.assets.load()

        self.reset()

    def reset(self) -> None:
        self.player = Player(self.assets.images["player"], self.assets.sounds.get("shoot"))
        self.player_bullet_image = self.assets.images["bullet"]
        self.enemy_bullet_image = self.assets.images["enemy_bullet"]
        self.enemies = EnemyFormation(self.assets.images["enemy"], self.enemy_bullet_image, self.assets.sounds.get("hit"))
        self.bullets: List[Bullet] = []
        self.explosions: List[Explosion] = []
        self.score = 0
        self.game_over = False

    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS)
            now_ms = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and self.game_over:
                    if event.key == pygame.K_RETURN:
                        self.reset()
                        self.game_over = False

            keys = pygame.key.get_pressed()
            if not self.game_over:
                self.update(now_ms, keys)
            self.draw()

    def update(self, now_ms: int, keys) -> None:
        # Player
        self.player.handle_input(keys)
        if keys[pygame.K_SPACE]:
            self.player.try_shoot(self.bullets, now_ms, self.player_bullet_image)

        # Enemies
        self.enemies.update(now_ms, self.bullets)

        # Bullets
        for b in self.bullets:
            if b.alive:
                b.update()
        self.bullets = [b for b in self.bullets if b.alive]

        # Collisions: player bullets vs enemies
        gained = self.enemies.check_collision_with_bullets(self.bullets)
        if gained:
            self.score += gained
            # Add a simple explosion where collision happened (approx: center of dead enemies)
            # For simplicity, we spawn explosions at bullets' positions that hit
            for b in [x for x in self.bullets if not x.alive and x.from_player]:
                self.explosions.append(Explosion([self.assets.images["explosion_1"], self.assets.images["explosion_2"]], b.rect.center))

        # Collisions: enemy bullets vs player
        for b in self.bullets:
            if b.alive and not b.from_player and self.player.rect.colliderect(b.rect):
                b.alive = False
                self.player.alive = False
                self.game_over = True
                if self.assets.sounds.get("game_over"):
                    self.assets.sounds["game_over"].play()
                self.explosions.append(Explosion([self.assets.images["explosion_1"], self.assets.images["explosion_2"]], self.player.rect.center))
                break

        if self.enemies.any_reached_bottom():
            self.player.alive = False
            self.game_over = True
            if self.assets.sounds.get("game_over"):
                self.assets.sounds["game_over"].play()

        if self.enemies.all_dead():
            # Respawn new wave and speed up a bit
            self.enemies = EnemyFormation(self.assets.images["enemy"], self.enemy_bullet_image, self.assets.sounds.get("hit"))

        # Effects
        for fx in self.explosions:
            if fx.alive:
                fx.update(now_ms)
        self.explosions = [fx for fx in self.explosions if fx.alive]

    def draw(self) -> None:
        self.screen.fill(COLOR_BG)

        # Draw entities
        if self.player.alive:
            self.screen.blit(self.player.image, self.player.rect)
        for e in self.enemies.enemies:
            if e.alive:
                self.screen.blit(e.image, e.rect)
        for b in self.bullets:
            img = self.player_bullet_image if b.from_player else self.enemy_bullet_image
            self.screen.blit(img, b.rect)
        for fx in self.explosions:
            fx.draw(self.screen)

        # HUD
        score_surf = self.font_small.render(f"Skor: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_surf, (10, 10))

        # Game Over overlay
        if self.game_over:
            over = self.font_large.render("GAME OVER", True, COLOR_WHITE)
            hint = self.font_small.render("Yeniden baslat: Enter", True, COLOR_WHITE)
            self.screen.blit(over, over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))

        pygame.display.flip()


