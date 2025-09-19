import os
import pygame
from typing import Tuple
from settings import IMAGES_DIR, SOUNDS_DIR, COLOR_GREEN, COLOR_RED, COLOR_YELLOW


class Assets:
    def __init__(self) -> None:
        self.images = {}
        self.sounds = {}

    def load(self) -> None:
        # Ensure mixer initialized; ignore if fails (no audio device)
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

        self.images["player"] = self._load_image("player.png", fallback=self._make_player_surface())
        self.images["enemy"] = self._load_image("enemy.png", fallback=self._make_enemy_surface())
        self.images["bullet"] = self._load_image("bullet.png", fallback=self._make_bullet_surface())
        self.images["enemy_bullet"] = self._load_image("enemy_bullet.png", fallback=self._make_enemy_bullet_surface())
        self.images["explosion_1"] = self._load_image("explosion_1.png", fallback=self._make_explosion_surface((255, 180, 60)))
        self.images["explosion_2"] = self._load_image("explosion_2.png", fallback=self._make_explosion_surface((255, 120, 60)))

        self.sounds["shoot"] = self._load_sound("shoot.wav")
        self.sounds["hit"] = self._load_sound("hit.wav")
        self.sounds["explosion"] = self._load_sound("explosion.wav")
        self.sounds["game_over"] = self._load_sound("game_over.wav")

    def _load_image(self, filename: str, fallback: pygame.Surface) -> pygame.Surface:
        path = os.path.join(IMAGES_DIR, filename)
        try:
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                return image
        except Exception:
            pass
        return fallback

    def _load_sound(self, filename: str):
        path = os.path.join(SOUNDS_DIR, filename)
        try:
            if os.path.exists(path) and pygame.mixer.get_init():
                return pygame.mixer.Sound(path)
        except Exception:
            pass
        return None

    def _make_player_surface(self) -> pygame.Surface:
        surf = pygame.Surface((44, 26), pygame.SRCALPHA)
        pygame.draw.polygon(surf, COLOR_GREEN, [(2, 24), (22, 2), (42, 24)])
        pygame.draw.rect(surf, (255, 255, 255), (20, 10, 4, 8))
        return surf

    def _make_enemy_surface(self) -> pygame.Surface:
        surf = pygame.Surface((36, 24), pygame.SRCALPHA)
        pygame.draw.rect(surf, COLOR_RED, (2, 6, 32, 12), border_radius=4)
        pygame.draw.rect(surf, (255, 255, 255), (8, 10, 4, 4))
        pygame.draw.rect(surf, (255, 255, 255), (24, 10, 4, 4))
        return surf

    def _make_bullet_surface(self) -> pygame.Surface:
        surf = pygame.Surface((4, 12), pygame.SRCALPHA)
        pygame.draw.rect(surf, COLOR_YELLOW, (0, 0, 4, 12))
        return surf

    def _make_enemy_bullet_surface(self) -> pygame.Surface:
        surf = pygame.Surface((4, 12), pygame.SRCALPHA)
        pygame.draw.rect(surf, (180, 200, 255), (0, 0, 4, 12))
        return surf

    def _make_explosion_surface(self, color: Tuple[int, int, int]) -> pygame.Surface:
        surf = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (14, 14), 12)
        pygame.draw.circle(surf, (255, 255, 255, 150), (14, 14), 6)
        return surf


