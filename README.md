# Painite Pocket

Full-colour Python 3 neon gravity chain-hoop arcade for [ElbowOS](https://x.com/ElbowOS).

Launch a mint ball from a copper spring. Gravity bends the arc. Thread three swaying rims for a chain. Bank off a backboard or clang a rim and the combo drops.

This is an original arcade, not a commercial basketball game and not a ROM.

## Play

```bash
pip install -r requirements.txt
python3 painite_pocket.py
```

- A / D or arrows — slide the spring
- W / S — aim
- Space — launch
- R — restart

## Record a 9:16 reel

```bash
python3 painite_pocket.py --record
```

Headless path uses `SDL_VIDEODRIVER=dummy`, draws a 1080x1920 surface, and pipes 15 seconds at 30fps to ffmpeg (`libx264`, `yuv420p`, CRF 20, `+faststart`).

## Links

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1FrmugSJQFjQ5EdaKzr-fh8lMPM5kuIMa/view
- Repo: https://github.com/ApacheAde/elbowos-painite-pocket
