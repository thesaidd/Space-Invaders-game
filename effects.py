import pygame
from typing import List


class Explosion:
    def __init__(self, frames: List[pygame.Surface], pos) -> None:
        self.frames = frames
        self.index = 0
        self.rect = self.frames[0].get_rect(center=pos)
        self.alive = True
        self.frame_time_ms = 60
        self.last_time = 0

    def update(self, now_ms: int) -> None:
        if now_ms - self.last_time >= self.frame_time_ms:
            self.last_time = now_ms
            self.index += 1
            if self.index >= len(self.frames):
                self.alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.alive and 0 <= self.index < len(self.frames):
            frame = self.frames[self.index]
            surface.blit(frame, self.rect)


