import sys
import pygame
from constants import *
from background import Background
from player import Player
from level import Level, PLAYER_START


# ── Sky gradient ───────────────────────────────────────────────────────────────

def draw_sky(surface, cam_y: float):
    """Interpolate sky colour from light-blue (ground) to deep-blue (summit)."""
    t = max(0.0, min(1.0, 1.0 - cam_y / LEVEL_HEIGHT))
    r = int(C_SKY_TOP[0] * t + C_SKY_BOT[0] * (1 - t))
    g = int(C_SKY_TOP[1] * t + C_SKY_BOT[1] * (1 - t))
    b = int(C_SKY_TOP[2] * t + C_SKY_BOT[2] * (1 - t))
    surface.fill((r, g, b))


# ── HUD ────────────────────────────────────────────────────────────────────────

def draw_hud(surface, font, score: int, total: int, height_pct: float):
    # Scroll counter
    txt = font.render(f"Scrolls  {score} / {total}", True, C_WHITE)
    surface.blit(txt, (10, 10))

    # Altitude bar (right edge, fills upward)
    BAR_H = 160
    bx, by, bw = WIDTH - 18, 10, 10
    pygame.draw.rect(surface, C_DARK, (bx, by, bw, BAR_H))
    fill = int(BAR_H * height_pct)
    pygame.draw.rect(surface, C_COLLECT, (bx, by + BAR_H - fill, bw, fill))
    pygame.draw.rect(surface, C_WHITE,   (bx, by, bw, BAR_H), 1)
    # Peak marker
    pygame.draw.rect(surface, C_COLLECT, (bx - 3, by, bw + 6, 3))

    # Controls hint — only shown near the start
    if height_pct < 0.04:
        hint = font.render(
            "SPACE jump · X/Shift scooter · hold SPACE (falling) glide",
            True, C_WHITE)
        surface.blit(hint, hint.get_rect(centerx=WIDTH // 2, bottom=HEIGHT - 8))


# ── Screen overlays ────────────────────────────────────────────────────────────

def draw_start(surface, font_big, font_sm):
    surface.fill(C_SKY_TOP)
    rows = [
        (font_big, "AIRBENDER SPIRES",                              C_WHITE),
        (font_sm,  "",                                              C_WHITE),
        (font_sm,  "Reach the peak of the Air Temple!",            C_WHITE),
        (font_sm,  "",                                              C_WHITE),
        (font_sm,  "Move      Arrow keys / WASD",                  C_WHITE),
        (font_sm,  "Jump      SPACE  (press again = double-jump)", C_WHITE),
        (font_sm,  "Glide     hold SPACE while falling",           C_WHITE),
        (font_sm,  "Scooter   X or Shift  (ground only)",          C_WHITE),
        (font_sm,  "",                                              C_WHITE),
        (font_sm,  "Press any key to begin",                       C_COLLECT),
    ]
    for i, (fnt, text, color) in enumerate(rows):
        if text:
            s = fnt.render(text, True, color)
            surface.blit(s, s.get_rect(center=(WIDTH // 2, 110 + i * 46)))


def draw_win(surface, font_big, font_sm, score: int, total: int):
    surface.fill(C_DARK)
    rows = [
        (font_big, "YOU REACHED THE TOP!",            C_COLLECT),
        (font_sm,  "",                                C_WHITE),
        (font_sm,  f"Air Scrolls collected:  {score} / {total}", C_WHITE),
        (font_sm,  "",                                C_WHITE),
        (font_sm,  "Press R to play again",           C_WHITE),
    ]
    for i, (fnt, text, color) in enumerate(rows):
        if text:
            s = fnt.render(text, True, color)
            surface.blit(s, s.get_rect(center=(WIDTH // 2, 240 + i * 58)))


def draw_dead_overlay(surface, font_big, font_sm):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((18, 18, 38, 185))
    surface.blit(ov, (0, 0))
    t1 = font_big.render("YOU FELL!", True, (255, 75, 75))
    t2 = font_sm.render( "Press R to restart", True, C_WHITE)
    surface.blit(t1, t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
    surface.blit(t2, t2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))


# ── Factory ────────────────────────────────────────────────────────────────────

def make_game():
    level  = Level()
    player = Player(*PLAYER_START)
    cam_y  = float(PLAYER_START[1] - HEIGHT // 2)
    return level, player, cam_y


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen   = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock    = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 36, bold=True)
    font_sm  = pygame.font.SysFont("Arial", 17)

    bg = Background()                          # generated once, never reset
    state = "start"
    level, player, cam_y = make_game()

    while True:
        events = pygame.event.get()
        keys   = pygame.key.get_pressed()

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ── START ──────────────────────────────────────────────────────────────
        if state == "start":
            draw_start(screen, font_big, font_sm)
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    state = "play"

        # ── PLAY ───────────────────────────────────────────────────────────────
        elif state == "play":
            if not player.dead:
                player.handle_input(events, keys)
                player.update(level.platforms, level.wind_currents)
                level.update()
                level.check_collect(player.rect)

                # Lerp camera toward player (slightly above centre)
                target = player.rect.centery - HEIGHT * 0.55
                target = max(0.0, min(float(LEVEL_HEIGHT - HEIGHT), target))
                cam_y += (target - cam_y) * CAM_LERP

                # ── Render ────────────────────────────────────────────────────
                draw_sky(screen, cam_y)
                bg.draw(screen, cam_y)          # parallax layers
                level.draw(screen, cam_y)
                player.draw(screen, cam_y)

                height_pct = 1.0 - max(0.0, min(1.0, player.rect.y / LEVEL_HEIGHT))
                draw_hud(screen, font_sm, level.score, level.total, height_pct)

                if level.check_finish(player.rect):
                    state = "win"

            else:
                # World frozen + overlay
                draw_sky(screen, cam_y)
                bg.draw(screen, cam_y)
                level.draw(screen, cam_y)
                player.draw(screen, cam_y)
                draw_dead_overlay(screen, font_big, font_sm)
                for ev in events:
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                        level, player, cam_y = make_game()

        # ── WIN ────────────────────────────────────────────────────────────────
        elif state == "win":
            draw_win(screen, font_big, font_sm, level.score, level.total)
            for ev in events:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    level, player, cam_y = make_game()
                    state = "play"

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
