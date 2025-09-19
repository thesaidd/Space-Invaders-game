# git (Pygame)

Basit bir Space Invaders tarzı 2D oyun. Uzay gemisi, mermi, düşmanlar; skor ve Game Over ekranı; ses efektleri ve basit animasyonlar içerir.

## Kurulum

1) Python 3.9+ kurulu olmalı.
2) Bağımlılığı yükleyin:

```bash
pip install -r requirements.txt
```

Alternatif:

```bash
pip install pygame
```

## Çalıştırma

```bash
python main.py
```

## Kontroller

- Sol/Yön veya `A`: Sola hareket
- Sağ/Yön veya `D`: Sağa hareket
- `Space`: Ateş et
- Game Over sonrası `Enter`: Yeniden başlat
- Menü:
  - `Enter`: Başla
  - `S`: Ayarlar
  - `Esc`: Çıkış
- Ayarlar:
  - `1/2/3`: Zorluk (Kolay/Normal/Zor)
  - `Sol/Sağ`: SFX ses ayarı
  - `Esc`: Menüye dön

## Assets Dizini

Görsel ve sesleri `assets` altında aşağıdaki gibi yerleştirin. Dosyalar yoksa oyun basit çizimlerle ve sessiz çalışır.

```
assets/
  images/
    player.png
    enemy.png
    bullet.png
    enemy_bullet.png
    explosion_1.png
    explosion_2.png
  sounds/
    shoot.wav
    hit.wav
    explosion.wav
    game_over.wav
```

## Yapı

- `settings.py`: Sabitler ve ayarlar
- `assets_loader.py`: Görsel/ses yükleyici, fallback çizimler
- `entities.py`: Oyuncu, mermi, düşman formasyonu, çarpışmalar
- `effects.py`: Patlama animasyonu
- `game.py`: Oyun döngüsü, skor, game over, çizimler
- Menü ve Ayarlar ekranları: `game.py` içinde durum (state) bazlı yönetim
- `main.py`: Giriş noktası

Not: Ses aygıtı yoksa oyun sessiz çalışabilir; görseller yoksa otomatik çizimler kullanılır.
