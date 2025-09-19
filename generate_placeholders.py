import os
import math
import wave
import struct
import pygame

IMAGES = [
    ("player.png", (44, 26)),
    ("enemy.png", (36, 24)),
    ("bullet.png", (4, 12)),
    ("enemy_bullet.png", (4, 12)),
    ("explosion_1.png", (28, 28)),
    ("explosion_2.png", (28, 28)),
]

SOUNDS = [
    ("shoot.wav", 660.0, 0.08),
    ("hit.wav", 330.0, 0.10),
    ("explosion.wav", 110.0, 0.25),
    ("game_over.wav", 220.0, 0.6),
]


def ensure_dirs() -> tuple[str, str]:
    images_dir = os.path.join("assets", "images")
    sounds_dir = os.path.join("assets", "sounds")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(sounds_dir, exist_ok=True)
    return images_dir, sounds_dir


def create_images(images_dir: str) -> None:
    pygame.init()
    for name, (w, h) in IMAGES:
        path = os.path.join(images_dir, name)
        if os.path.exists(path):
            continue
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        if name == "player.png":
            pygame.draw.polygon(surf, (80, 220, 120), [(2, h - 2), (w // 2, 2), (w - 2, h - 2)])
            pygame.draw.rect(surf, (255, 255, 255), (w // 2 - 2, h // 2 - 4, 4, 8))
        elif name == "enemy.png":
            pygame.draw.rect(surf, (230, 80, 80), (2, 6, w - 4, h - 12), border_radius=4)
            pygame.draw.rect(surf, (255, 255, 255), (8, h // 2 - 2, 4, 4))
            pygame.draw.rect(surf, (255, 255, 255), (w - 12, h // 2 - 2, 4, 4))
        elif name == "bullet.png":
            pygame.draw.rect(surf, (250, 220, 70), (0, 0, w, h))
        elif name == "enemy_bullet.png":
            pygame.draw.rect(surf, (180, 200, 255), (0, 0, w, h))
        elif name == "explosion_1.png":
            pygame.draw.circle(surf, (255, 180, 60), (w // 2, h // 2), min(w, h) // 2 - 2)
            pygame.draw.circle(surf, (255, 255, 255, 160), (w // 2, h // 2), min(w, h) // 4)
        elif name == "explosion_2.png":
            pygame.draw.circle(surf, (255, 120, 60), (w // 2, h // 2), min(w, h) // 2 - 2)
            pygame.draw.circle(surf, (255, 240, 200, 160), (w // 2, h // 2), min(w, h) // 5)
        pygame.image.save(surf, path)


def sine_wave(frequency: float, duration_s: float, sample_rate: int = 44100, volume: float = 0.4):
    num_samples = int(duration_s * sample_rate)
    for i in range(num_samples):
        t = i / sample_rate
        # simple decay envelope
        env = max(0.0, 1.0 - t / duration_s)
        sample = math.sin(2 * math.pi * frequency * t) * env * volume
        yield int(sample * 32767)


def create_wav(path: str, frequency: float, duration_s: float) -> None:
    if os.path.exists(path):
        return
    sample_rate = 44100
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        frames = b''.join(struct.pack('<h', s) for s in sine_wave(frequency, duration_s, sample_rate))
        wf.writeframes(frames)


def create_sounds(sounds_dir: str) -> None:
    for name, freq, dur in SOUNDS:
        path = os.path.join(sounds_dir, name)
        create_wav(path, freq, dur)


def main() -> None:
    images_dir, sounds_dir = ensure_dirs()
    create_images(images_dir)
    create_sounds(sounds_dir)
    print("Placeholder assets generated (where missing).")


if __name__ == "__main__":
    main()


