import sys
import pygame
import scores as scoreboard
from constants import *
from background import Background
from player import Player
from level import ProceduralLevel


# ── Sky gradient ───────────────────────────────────────────────────────────────

def draw_sky(surface, cam_y: float):
    """Three-stop gradient: low=light blue, mid=blue, high=deep blue."""
    altitude = max(0.0, PLAYER_START_Y - cam_y)
    t = min(1.0, altitude / 3800)
    if t < 0.5:
        s = t * 2
        r = int(C_SKY_LOW[0] * (1 - s) + C_SKY_MID[0] * s)
        g = int(C_SKY_LOW[1] * (1 - s) + C_SKY_MID[1] * s)
        b = int(C_SKY_LOW[2] * (1 - s) + C_SKY_MID[2] * s)
    else:
        s = (t - 0.5) * 2
        r = int(C_SKY_MID[0] * (1 - s) + C_SKY_HIGH[0] * s)
        g = int(C_SKY_MID[1] * (1 - s) + C_SKY_HIGH[1] * s)
        b = int(C_SKY_MID[2] * (1 - s) + C_SKY_HIGH[2] * s)
    surface.fill((r, g, b))


# ── HUD ────────────────────────────────────────────────────────────────────────

def draw_hud(surface, font, score: int, scroll_count: int, scroll_speed: float):
    # Score
    surface.blit(font.render(f"Score  {score:,}", True, C_WHITE), (10, 10))
    # Scrolls
    surface.blit(font.render(f"Scrolls  {scroll_count}", True, C_GOLD), (10, 32))

    # Speed level bar (right side)
    BAR_H = 120
    bx, by, bw = WIDTH - 18, 10, 10
    t = min(1.0, (scroll_speed - SCROLL_SPEED_START) /
                  (SCROLL_SPEED_MAX - SCROLL_SPEED_START))
    fill = int(BAR_H * t)
    col  = (
        int(100 + 155 * t),   # R increases with speed
        int(220 - 150 * t),   # G decreases
        int(255 - 200 * t),   # B decreases
    )
    pygame.draw.rect(surface, C_DARK,  (bx, by, bw, BAR_H))
    pygame.draw.rect(surface, col,     (bx, by + BAR_H - fill, bw, fill))
    pygame.draw.rect(surface, C_WHITE, (bx, by, bw, BAR_H), 1)
    spd_lbl = font.render("spd", True, C_WHITE)
    surface.blit(spd_lbl, spd_lbl.get_rect(centerx=bx + bw // 2, top=by + BAR_H + 4))

    # Controls hint on first few seconds
    if scroll_speed < SCROLL_SPEED_START + 0.05:
        hint = font.render(
            "SPACE jump · double-jump · hold=glide · X/Shift=scooter",
            True, C_WHITE)
        surface.blit(hint, hint.get_rect(centerx=WIDTH // 2, bottom=HEIGHT - 8))


# ── Overlays ───────────────────────────────────────────────────────────────────

def draw_start(surface, font_big, font_sm, board: list):
    surface.fill(C_SKY_MID)
    rows = [
        (font_big, "AIRBENDER SPIRES",                             C_WHITE),
        (font_sm,  "",                                             C_WHITE),
        (font_sm,  "Climb the temple. Survive the scroll.",        C_WHITE),
        (font_sm,  "",                                             C_WHITE),
        (font_sm,  "Move   Arrow / WASD      Jump   SPACE",        C_WHITE),
        (font_sm,  "Double-jump   SPACE (air)   Glide   hold SPACE (falling)", C_WHITE),
        (font_sm,  "Air Scooter   X / Shift  (ground)",            C_WHITE),
    ]
    if board:
        rows += [(font_sm, "", C_WHITE),
                 (font_sm, f"Top score:  {board[0]['name']}  {board[0]['score']:,}", C_GOLD)]
    rows += [(font_sm, "", C_WHITE), (font_sm, "Press any key to start", C_GOLD)]

    for i, (fnt, text, color) in enumerate(rows):
        if text:
            s = fnt.render(text, True, color)
            surface.blit(s, s.get_rect(center=(WIDTH // 2, 90 + i * 44)))


def draw_name_entry(surface, font_big, font_sm, score: int, name: str, blink: bool):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((18, 18, 38, 210))
    surface.blit(ov, (0, 0))
    lines = [
        (font_big, "GAME OVER",           (255, 80, 80)),
        (font_sm,  f"Score:  {score:,}",  C_GOLD),
        (font_sm,  "",                    C_WHITE),
        (font_sm,  "Enter your name:",    C_WHITE),
        (font_big, name + ("|" if blink else " "), C_WHITE),
        (font_sm,  "",                    C_WHITE),
        (font_sm,  "Press Enter to save", C_WHITE),
    ]
    for i, (fnt, text, color) in enumerate(lines):
        if text:
            s = fnt.render(text, True, color)
            surface.blit(s, s.get_rect(center=(WIDTH // 2, 180 + i * 56)))


def draw_leaderboard(surface, font_big, font_sm, board: list, highlight: str):
    surface.fill(C_DARK)
    surface.blit(font_big.render("LEADERBOARD", True, C_GOLD),
                 font_big.render("LEADERBOARD", True, C_GOLD)
                 .get_rect(center=(WIDTH // 2, 50)))
    for rank, entry in enumerate(board, 1):
        name   = entry["name"]
        pts    = entry["score"]
        color  = C_GOLD if name == highlight else C_WHITE
        line   = font_sm.render(f"#{rank:<2}  {name:<12} {pts:>8,}", True, color)
        surface.blit(line, line.get_rect(center=(WIDTH // 2, 110 + rank * 42)))
    footer = font_sm.render("R = play again     Esc = title", True, C_WHITE)
    surface.blit(footer, footer.get_rect(center=(WIDTH // 2, HEIGHT - 30)))


# ── Game factory ───────────────────────────────────────────────────────────────

def make_game():
    level        = ProceduralLevel()
    player       = Player(PLAYER_START_X, PLAYER_START_Y)
    cam_y        = float(PLAYER_START_Y - HEIGHT * 0.55)
    ideal_cam_y  = cam_y
    scroll_speed = SCROLL_SPEED_START
    scroll_count = 0
    return level, player, cam_y, ideal_cam_y, scroll_speed, scroll_count


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen   = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock    = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 36, bold=True)
    font_sm  = pygame.font.SysFont("Arial", 17)

    bg    = Background()
    board = scoreboard.load()

    state = "start"
    level, player, cam_y, ideal_cam_y, scroll_speed, scroll_count = make_game()

    # Scoring state
    score        = 0
    final_score  = 0
    name_input   = ""
    last_name    = ""
    blink_timer  = 0

    while True:
        events = pygame.event.get()
        keys   = pygame.key.get_pressed()

        for ev in events:
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ── START ──────────────────────────────────────────────────────────────
        if state == "start":
            draw_start(screen, font_big, font_sm, board)
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    level, player, cam_y, ideal_cam_y, scroll_speed, scroll_count = make_game()
                    score = 0
                    state = "play"

        # ── PLAY ───────────────────────────────────────────────────────────────
        elif state == "play":
            # Auto-scroll: ideal camera creeps upward at increasing speed
            scroll_speed  = min(scroll_speed + SCROLL_ACCEL, SCROLL_SPEED_MAX)
            ideal_cam_y  -= scroll_speed

            player.handle_input(events, keys)
            player.update(level.platforms, level.wind_currents, level.bisons)
            level.update(cam_y)

            new_scrolls  = level.check_collect(player.rect)
            scroll_count += new_scrolls

            # Score: height climbed + scroll bonuses
            height_gained = max(0, PLAYER_START_Y - player.rect.y)
            score = int(height_gained / HEIGHT_DIVISOR) + scroll_count * SCROLL_POINTS

            # Camera: follow player OR scroll, whichever is higher
            player_cam  = player.rect.centery - HEIGHT * 0.55
            target      = min(ideal_cam_y, player_cam)
            cam_y      += (target - cam_y) * CAM_LERP

            # Death: player fell below visible area
            if player.rect.top > cam_y + HEIGHT + 30:
                player.dead = True

            # Render
            draw_sky(screen, cam_y)
            bg.draw(screen, cam_y)
            level.draw(screen, cam_y)
            player.draw(screen, cam_y)
            draw_hud(screen, font_sm, score, scroll_count, scroll_speed)

            if player.dead:
                final_score = score
                name_input  = ""
                blink_timer = 0
                state       = "name_entry"

        # ── NAME ENTRY ─────────────────────────────────────────────────────────
        elif state == "name_entry":
            blink_timer += 1
            blink = (blink_timer // 30) % 2 == 0

            # World still visible behind overlay
            draw_sky(screen, cam_y)
            bg.draw(screen, cam_y)
            level.draw(screen, cam_y)
            player.draw(screen, cam_y)
            draw_name_entry(screen, font_big, font_sm, final_score, name_input, blink)

            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN and name_input.strip():
                        last_name = name_input.strip().upper()
                        board = scoreboard.add(last_name, final_score)
                        state = "leaderboard"
                    elif ev.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    elif len(name_input) < 10 and ev.unicode.isprintable() and ev.unicode.strip():
                        name_input += ev.unicode.upper()

        # ── LEADERBOARD ────────────────────────────────────────────────────────
        elif state == "leaderboard":
            draw_leaderboard(screen, font_big, font_sm, board, last_name)
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_r:
                        level, player, cam_y, ideal_cam_y, scroll_speed, scroll_count = make_game()
                        score = 0
                        state = "play"
                    elif ev.key == pygame.K_ESCAPE:
                        state = "start"

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
