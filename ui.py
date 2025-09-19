import pygame
from typing import Callable, Tuple


def draw_panel(surface: pygame.Surface, rect: pygame.Rect, bg: Tuple[int, int, int], border: Tuple[int, int, int] | None = None, radius: int = 12, border_width: int = 2):
    pygame.draw.rect(surface, bg, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, width=border_width, border_radius=radius)


class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, on_click: Callable[[], None],
                 color_bg=(30, 30, 50), color_fg=(240, 240, 240), color_hover=(50, 50, 80)) -> None:
        self.rect = rect
        self.text = text
        self.font = font
        self.on_click = on_click
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.color_hover = color_hover
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, surface: pygame.Surface, focused: bool = False) -> None:
        bg = self.color_hover if (self.hovered or focused) else self.color_bg
        border_color = (140, 140, 200) if focused else (90, 90, 130)
        draw_panel(surface, self.rect, bg, border=border_color)
        label = self.font.render(self.text, True, self.color_fg)
        surface.blit(label, label.get_rect(center=self.rect.center))
        if focused:
            # draw a small triangle indicator on the left
            tip_y = self.rect.centery
            x0 = self.rect.left - 14
            points = [(x0 + 10, tip_y), (x0 + 2, tip_y - 6), (x0 + 2, tip_y + 6)]
            pygame.draw.polygon(surface, border_color, points)


class Slider:
    def __init__(self, rect: pygame.Rect, value: float, on_change: Callable[[float], None],
                 track_color=(60, 60, 90), fill_color=(120, 180, 255), knob_color=(240, 240, 240)) -> None:
        self.rect = rect
        self.value = max(0.0, min(1.0, value))
        self.on_change = on_change
        self.track_color = track_color
        self.fill_color = fill_color
        self.knob_color = knob_color
        self.dragging = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value_from_pos(event.pos[0])

    def _update_value_from_pos(self, x: int) -> None:
        left, width = self.rect.x, self.rect.w
        t = (x - left) / max(1, width)
        self.value = max(0.0, min(1.0, t))
        self.on_change(self.value)

    def draw(self, surface: pygame.Surface, focused: bool = False) -> None:
        # Track
        track_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.h // 2 - 4, self.rect.w, 8)
        pygame.draw.rect(surface, self.track_color, track_rect, border_radius=4)
        # Fill
        fill_rect = track_rect.copy()
        fill_rect.w = int(self.value * self.rect.w)
        pygame.draw.rect(surface, self.fill_color, fill_rect, border_radius=4)
        # Knob
        knob_x = self.rect.x + int(self.value * self.rect.w)
        knob_rect = pygame.Rect(knob_x - 8, self.rect.y + self.rect.h // 2 - 12, 16, 24)
        pygame.draw.rect(surface, self.knob_color, knob_rect, border_radius=6)
        if focused:
            pygame.draw.rect(surface, (140, 140, 200), self.rect, width=2, border_radius=8)


