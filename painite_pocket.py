#!/usr/bin/env python3
"""Painite Pocket — gravity chain-hoop arcade for ElbowOS.

Thread a mint ball through three swaying copper rims. Gravity pulls every shot.
A / D or arrows move the spring. W / S aim. Space launches. R restarts.

  python3 painite_pocket.py           # windowed play
  python3 painite_pocket.py --record  # 15s 1080x1920 autoplay MP4
"""
import math
import os
import random
import subprocess
import sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOW_RECORD") == "1"
if RECORD:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

W, H = 1080, 1920
FPS = 30
OUT = os.environ.get("ELBOW_OUT", "PainitePocket_ElbowOS.mp4")
BG, COURT = (36, 10, 24), (88, 24, 46)
LINE, BALL_C, RIM = (255, 176, 92), (110, 255, 190), (255, 118, 42)
BACK, TEXT = (255, 214, 140), (255, 236, 210)


class Game:
    def __init__(self, auto=False):
        self.auto = auto
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.combo = 0
        self.balls = 8
        self.pad_x = W / 2
        self.angle = -1.2
        self.ball = None
        self.sparks = []
        self.flash = 0
        self.msg = "SPACE LAUNCH"
        self.hoops = [
            {"y": 430, "phase": 0.2, "amp": 230, "scored": False},
            {"y": 780, "phase": 2.1, "amp": 270, "scored": False},
            {"y": 1130, "phase": 3.8, "amp": 210, "scored": False},
        ]
        self.next_launch = 12

    def hoop_x(self, h):
        return W / 2 + math.sin(self.t * 0.05 + h["phase"]) * h["amp"]

    def launch(self, ang=None, pwr=28.0):
        if self.ball or self.balls <= 0:
            return
        ang = self.angle if ang is None else ang
        self.ball = {
            "x": self.pad_x, "y": 1668.0, "vx": math.cos(ang) * pwr,
            "vy": math.sin(ang) * pwr, "r": 30, "through": set(),
        }
        self.balls -= 1
        self.msg = "IN FLIGHT"

    def update(self, keys=None):
        self.t += 1
        self.flash = max(0, self.flash - 1)
        if not self.auto and keys:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.pad_x -= 16
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.pad_x += 16
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.angle -= 0.035
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.angle += 0.035
            self.pad_x = max(150, min(W - 150, self.pad_x))
            self.angle = max(-2.6, min(-0.45, self.angle))
        if self.auto:
            goal = next((h for h in self.hoops if not h["scored"]), self.hoops[0])
            self.pad_x += max(-18, min(18, (self.hoop_x(goal) - self.pad_x) * 0.09))
            self.next_launch -= 1
            if self.ball is None and self.next_launch <= 0 and self.balls > 0:
                gx = self.hoop_x(goal) + random.uniform(-36, 36)
                ang = math.atan2(goal["y"] - 1668, gx - self.pad_x) - 0.28
                self.angle = max(-2.35, min(-0.7, ang))
                self.launch(self.angle, random.uniform(27, 33))
                self.next_launch = random.randint(48, 70)
            if self.balls <= 0 and self.ball is None:
                self.balls = 8
                self.msg = "NEW RACK"
        b = self.ball
        if b:
            b["vy"] += 0.46
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            if b["x"] < 78 or b["x"] > W - 78:
                b["vx"] *= -0.84
                b["x"] = max(78, min(W - 78, b["x"]))
            for i, h in enumerate(self.hoops):
                hx, hy, rw = self.hoop_x(h), h["y"], 122
                if abs(b["y"] - hy) < 28 and i not in b["through"]:
                    if abs(b["x"] - (hx - rw)) < 24 or abs(b["x"] - (hx + rw)) < 24:
                        b["vx"] *= -0.72
                        b["vy"] *= -0.4
                    elif abs(b["x"] - hx) < rw - 20 and b["vy"] > 1:
                        b["through"].add(i)
                        if not h["scored"]:
                            h["scored"] = True
                            self.combo += 1
                            self.score += 100 * self.combo
                            self.flash = 8
                            self.msg = f"POCKET x{self.combo}"
                            for _ in range(12):
                                self.sparks.append([
                                    b["x"], b["y"], random.uniform(-7, 7),
                                    random.uniform(-9, 1), 16,
                                ])
                if abs(b["x"] - (hx + rw + 40)) < 18 and abs(b["y"] - (hy - 60)) < 100 and b["vx"] > 0:
                    b["vx"] *= -0.78
            if all(h["scored"] for h in self.hoops):
                for h in self.hoops:
                    h["scored"] = False
                self.combo += 1
                self.score += 250
                self.balls = min(9, self.balls + 1)
                self.msg = "CHAIN CLEAR"
            if b["y"] > 1840:
                self.ball = None
                self.combo = 0
                self.msg = "AIRBALL"
                if not self.auto and self.balls <= 0:
                    self.reset()
        self.sparks = [s for s in self.sparks if s[4] > 0]
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[4] -= 1

    def draw(self, surf, font, big, small):
        surf.fill(BG)
        pygame.draw.rect(surf, COURT, (46, 270, W - 92, 1490), border_radius=30)
        for i in range(9):
            pygame.draw.line(surf, (124, 42, 66), (68, 330 + i * 150), (W - 68, 330 + i * 150), 2)
        pygame.draw.rect(surf, (70, 18, 36), (W // 2 - 170, 1288, 340, 400), 5, border_radius=14)
        pygame.draw.circle(surf, LINE, (W // 2, 1500), 156, 5)
        for h in self.hoops:
            hx, hy = int(self.hoop_x(h)), h["y"]
            col = (255, 214, 80) if h["scored"] else RIM
            pygame.draw.rect(surf, BACK, (hx + 108, hy - 140, 20, 190), border_radius=4)
            pygame.draw.rect(surf, (255, 80, 64), (hx + 112, hy - 78, 12, 78))
            for k in range(-4, 5):
                pygame.draw.line(surf, (255, 232, 196), (hx - 104 + k * 26, hy + 10), (hx - 36 + k * 10, hy + 78), 3)
            pygame.draw.ellipse(surf, col, (hx - 126, hy - 16, 252, 32), 7)
        px = int(self.pad_x)
        pygame.draw.rect(surf, (255, 146, 64), (px - 78, 1710, 156, 26), border_radius=10)
        pygame.draw.circle(surf, (255, 206, 130), (px, 1722), 18)
        ex = px + math.cos(self.angle) * 120
        ey = 1668 + math.sin(self.angle) * 120
        pygame.draw.line(surf, (255, 236, 186), (px, 1694), (ex, ey), 7)
        if self.ball:
            b = self.ball
            pygame.draw.circle(surf, (18, 50, 36), (int(b["x"]) + 5, int(b["y"]) + 7), b["r"])
            pygame.draw.circle(surf, BALL_C, (int(b["x"]), int(b["y"])), b["r"])
            pygame.draw.circle(surf, (230, 255, 236), (int(b["x"]) - 9, int(b["y"]) - 9), 9)
        else:
            pygame.draw.circle(surf, BALL_C, (int(ex), int(ey)), 14)
        for s in self.sparks:
            pygame.draw.circle(surf, (255, 196, 70), (int(s[0]), int(s[1])), 5)
        title = big.render("PAINITE POCKET", True, TEXT)
        surf.blit(title, (W // 2 - title.get_width() // 2, 62))
        sub = small.render("GRAVITY CHAIN HOOPS", True, LINE)
        surf.blit(sub, (W // 2 - sub.get_width() // 2, 150))
        surf.blit(font.render(f"SCORE {self.score}", True, (255, 244, 200)), (64, 214))
        balls = font.render(f"BALLS {self.balls}", True, (170, 255, 206))
        surf.blit(balls, (W - 64 - balls.get_width(), 214))
        note = small.render(self.msg, True, (255, 210, 150))
        surf.blit(note, (W // 2 - note.get_width() // 2, 1762))
        tag = font.render("x.com/ElbowOS", True, (255, 186, 120))
        surf.blit(tag, (W // 2 - tag.get_width() // 2, 1828))
        if self.flash:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((255, 170, 50, 46))
            surf.blit(veil, (0, 0))


def main():
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(None, 64)
    big = pygame.font.Font(None, 92)
    small = pygame.font.Font(None, 42)
    if RECORD:
        surf = pygame.Surface((W, H))
        game = Game(auto=True)
        random.seed(7)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
            "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        if proc.stdin is None:
            raise SystemExit("ffmpeg stdin missing")
        try:
            for _ in range(FPS * 15):
                game.update()
                game.draw(surf, font, big, small)
                proc.stdin.write(pygame.image.tobytes(surf, "RGB"))
        finally:
            proc.stdin.close()
            code = proc.wait()
        if code != 0:
            raise SystemExit(f"ffmpeg failed: {code}")
        print("WROTE", OUT)
        return
    screen = pygame.display.set_mode((540, 960))
    pygame.display.set_caption("Painite Pocket — ElbowOS")
    canvas = pygame.Surface((W, H))
    clock = pygame.time.Clock()
    game = Game(False)
    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    game.launch()
                elif event.key == pygame.K_r:
                    game.reset()
        game.update(keys)
        game.draw(canvas, font, big, small)
        screen.blit(pygame.transform.smoothscale(canvas, (540, 960)), (0, 0))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
