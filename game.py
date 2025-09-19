import pygame
from typing import List
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    COLOR_BG,
    COLOR_WHITE,
    WINDOW_TITLE,
    DEFAULT_SFX_VOLUME,
    DIFFICULTY_PRESETS,
)
from assets_loader import Assets
from entities import Player, Bullet, EnemyFormation
from effects import Explosion
from ui import Button, Slider, draw_panel


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_large = pygame.font.SysFont("Arial", 40)
        self.font_small = pygame.font.SysFont("Arial", 24)
        self.font_medium = pygame.font.SysFont("Arial", 30)

        self.assets = Assets()
        self.assets.load()
        # Apply default volume
        vol = DEFAULT_SFX_VOLUME
        for s in self.assets.sounds.values():
            if s:
                s.set_volume(vol)

        # Game state
        self.state = "menu"  # menu | settings | playing | game_over
        self.level = 1
        self.sfx_volume = DEFAULT_SFX_VOLUME
        self.difficulty = "Normal"
        self.reset()
        self._build_ui()
        self.menu_focus_idx = 0
        self.settings_focus_idx = 0  # 0..2 difficulty buttons, 3 back, 4 slider

    def reset(self) -> None:
        self.player = Player(self.assets.images["player"], self.assets.sounds.get("shoot"))
        self.player_bullet_image = self.assets.images["bullet"]
        self.enemy_bullet_image = self.assets.images["enemy_bullet"]
        self.enemies = EnemyFormation(self.assets.images["enemy"], self.enemy_bullet_image, self.assets.sounds.get("hit"))
        self._apply_difficulty_to_enemies()
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
                if event.type == pygame.KEYDOWN:
                    if self.state == "menu":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.menu_focus_idx = (self.menu_focus_idx - 1) % len(self.menu_buttons)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.menu_focus_idx = (self.menu_focus_idx + 1) % len(self.menu_buttons)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            # activate focused
                            self._activate_menu_button(self.menu_focus_idx)
                        elif event.key == pygame.K_ESCAPE:
                            return
                    elif self.state == "settings":
                        if event.key in (pygame.K_LEFT, pygame.K_a):
                            if self.settings_focus_idx == 4:
                                self._set_volume(max(0.0, round(self.sfx_volume - 0.05, 2)))
                            else:
                                self.settings_focus_idx = (self.settings_focus_idx - 1) % 5
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            if self.settings_focus_idx == 4:
                                self._set_volume(min(1.0, round(self.sfx_volume + 0.05, 2)))
                            else:
                                self.settings_focus_idx = (self.settings_focus_idx + 1) % 5
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            # move to top row (difficulty buttons)
                            if self.settings_focus_idx >= 3:
                                self.settings_focus_idx = 1
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            # move to bottom controls (back and slider)
                            if self.settings_focus_idx < 3:
                                self.settings_focus_idx = 3
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self._activate_settings_control(self.settings_focus_idx)
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "menu"
                    elif self.state == "game_over":
                        if event.key == pygame.K_RETURN:
                            self.level = 1
                            self.reset()
                            self.state = "playing"
                        elif event.key == pygame.K_ESCAPE:
                            self.state = "menu"

            # Keyboard-only mode: do not drain event queue again for mouse

            keys = pygame.key.get_pressed()
            if self.state == "playing" and not self.game_over:
                self.update(now_ms, keys)
            self.draw()

    def _apply_difficulty_to_enemies(self) -> None:
        preset = DIFFICULTY_PRESETS.get(self.difficulty, DIFFICULTY_PRESETS["Normal"])
        self.enemies.move_interval_ms = preset["enemy_move_interval_ms"]
        self.enemies.shoot_chance = preset["enemy_shoot_chance"]
        # scale by level (increase challenge as level rises)
        if self.level > 1:
            self.enemies.move_interval_ms = max(100, int(self.enemies.move_interval_ms * (0.94 ** (self.level - 1))))
            self.enemies.shoot_chance *= (1.06 ** (self.level - 1))

    def _set_difficulty(self, name: str) -> None:
        self.difficulty = name
        self._apply_difficulty_to_enemies()
        # provide subtle feedback via volume-adjusted click if available
        if self.assets.sounds.get("hit"):
            snd = self.assets.sounds["hit"]
            prev = snd.get_volume()
            snd.set_volume(min(1.0, self.sfx_volume))
            snd.play()
            snd.set_volume(prev)

    def _set_volume(self, value: float) -> None:
        self.sfx_volume = value
        for s in self.assets.sounds.values():
            if s:
                s.set_volume(self.sfx_volume)

    def _build_ui(self) -> None:
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        btn_w, btn_h = 260, 54
        spacing = 16
        # Menu buttons
        def start_game():
            self.level = 1
            self.reset()
            self.state = "playing"

        def go_settings():
            self.state = "settings"

        def exit_game():
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        self.menu_buttons = [
            Button(pygame.Rect(cx - btn_w // 2, cy - btn_h - spacing, btn_w, btn_h), "Basla", self.font_medium, start_game),
            Button(pygame.Rect(cx - btn_w // 2, cy, btn_w, btn_h), "Ayarlar", self.font_medium, go_settings),
            Button(pygame.Rect(cx - btn_w // 2, cy + btn_h + spacing, btn_w, btn_h), "Cikis", self.font_medium, exit_game),
        ]

        # Settings buttons
        diff_w = 180
        y0 = cy - 40
        self.settings_buttons = [
            Button(pygame.Rect(cx - diff_w - 100, y0, diff_w, 48), "Kolay", self.font_small, lambda: self._set_difficulty("Kolay")),
            Button(pygame.Rect(cx - diff_w // 2, y0, diff_w, 48), "Normal", self.font_small, lambda: self._set_difficulty("Normal")),
            Button(pygame.Rect(cx + 100, y0, diff_w, 48), "Zor", self.font_small, lambda: self._set_difficulty("Zor")),
            Button(pygame.Rect(cx - 90, cy + 90, 180, 48), "Menu", self.font_small, lambda: setattr(self, "state", "menu")),
        ]

        # Volume slider
        self.volume_slider = Slider(pygame.Rect(cx - 200, cy + 30, 400, 30), self.sfx_volume, self._set_volume)

    def _activate_menu_button(self, idx: int) -> None:
        if idx == 0:
            self.level = 1
            self.reset()
            self.state = "playing"
        elif idx == 1:
            self.state = "settings"
        elif idx == 2:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _activate_settings_control(self, idx: int) -> None:
        if idx == 0:
            self._set_difficulty("Kolay")
        elif idx == 1:
            self._set_difficulty("Normal")
        elif idx == 2:
            self._set_difficulty("Zor")
        elif idx == 3:
            self.state = "menu"
        # idx 4 is slider; activation not needed

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
            # Next level: increase difficulty a bit each level
            self.level += 1
            self.enemies = EnemyFormation(self.assets.images["enemy"], self.enemy_bullet_image, self.assets.sounds.get("hit"))
            # Re-apply difficulty + level scaling
            self._apply_difficulty_to_enemies()

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

        # HUD or Screens
        if self.state == "playing":
            score_surf = self.font_small.render(f"Skor: {self.score}", True, COLOR_WHITE)
            level_surf = self.font_small.render(f"Seviye: {self.level}", True, COLOR_WHITE)
            self.screen.blit(score_surf, (10, 10))
            self.screen.blit(level_surf, (10, 36))
            if self.game_over:
                over = self.font_large.render("GAME OVER", True, COLOR_WHITE)
                hint = self.font_small.render("Enter: Yeniden baslat | Esc: Menu", True, COLOR_WHITE)
                self.screen.blit(over, over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
                self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))
                self.state = "game_over"
        elif self.state == "menu":
            # Background panel
            panel = pygame.Rect(SCREEN_WIDTH // 2 - 260, SCREEN_HEIGHT // 2 - 160, 520, 320)
            draw_panel(self.screen, panel, (20, 20, 40), border=(80, 80, 120))
            title = self.font_large.render("Space Invaders", True, COLOR_WHITE)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, panel.y + 44)))
            for i, b in enumerate(self.menu_buttons):
                b.draw(self.screen, focused=(i == self.menu_focus_idx))
        elif self.state == "settings":
            panel = pygame.Rect(SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 180, 600, 360)
            draw_panel(self.screen, panel, (20, 20, 40), border=(80, 80, 120))
            title = self.font_large.render("Ayarlar", True, COLOR_WHITE)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, panel.y + 40)))
            sub = self.font_small.render(f"Zorluk: {self.difficulty}", True, COLOR_WHITE)
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, panel.y + 90)))
            for i, b in enumerate(self.settings_buttons):
                b.draw(self.screen, focused=(i == self.settings_focus_idx))
            # Volume
            vol_label = self.font_small.render(f"SFX Ses: {int(self.sfx_volume * 100)}%", True, COLOR_WHITE)
            self.screen.blit(vol_label, vol_label.get_rect(center=(SCREEN_WIDTH // 2, panel.y + 160)))
            self.volume_slider.draw(self.screen, focused=(self.settings_focus_idx == 4))

        pygame.display.flip()


