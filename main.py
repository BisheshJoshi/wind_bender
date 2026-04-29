import sys
import pygame
import scores as scoreboard
from constants import *
from background import Background
from player import Player
from level import ProceduralLevel, _zone_from_alt


# ── Zone ───────────────────────────────────────────────────────────────────────

def current_zone(player_y: float) -> int:
    return _zone_from_alt(max(0.0, PLAYER_START_Y - player_y))


# ── Sky gradient ───────────────────────────────────────────────────────────────

def draw_sky(surface, cam_y: float, zone: int):
    high_col, low_col = ZONE_SKY[zone]
    altitude = max(0.0, PLAYER_START_Y - cam_y)
    # Within-zone progress 0→1
    lo = ZONE_ALTS[zone]
    hi = ZONE_ALTS[zone + 1] if zone + 1 < len(ZONE_ALTS) else lo + 1600
    t  = min(1.0, max(0.0, (altitude - lo) / (hi - lo)))
    r = int(low_col[0] * (1 - t) + high_col[0] * t)
    g = int(low_col[1] * (1 - t) + high_col[1] * t)
    b = int(low_col[2] * (1 - t) + high_col[2] * t)
    surface.fill((r, g, b))


# ── HUD ────────────────────────────────────────────────────────────────────────

def draw_hud(surface, font, font_sm, score: int, scroll_count: int,
             health: int, blast_cd: int, zone: int, zone_timer: int):
    # Health — chi swirls (filled circles = alive, dim = lost)
    for i in range(PLAYER_MAX_HEALTH):
        col = C_HEALTH_ON if i < health else C_HEALTH_OFF
        cx  = 18 + i * 26
        pygame.draw.circle(surface, col, (cx, 18), 10)
        pygame.draw.circle(surface, C_WHITE, (cx, 18), 10, 1)
        # Inner swirl dot
        pygame.draw.circle(surface, C_WHITE if i < health else C_DARK, (cx, 18), 4)

    # Score
    surface.blit(font.render(f"{score:,}", True, C_WHITE), (10, 38))

    # Scrolls
    surface.blit(font_sm.render(f"Scrolls  {scroll_count}", True, C_GOLD), (10, 62))

    # Blast cooldown bar
    if blast_cd > 0:
        bar_w = int((WIDTH // 3) * (1 - blast_cd / BLAST_COOLDOWN))
        pygame.draw.rect(surface, C_WIND_GLOW, (10, HEIGHT - 22, bar_w, 8))
        pygame.draw.rect(surface, C_WHITE, (10, HEIGHT - 22, WIDTH // 3, 8), 1)
        lbl = font_sm.render("blast", True, C_WHITE)
        surface.blit(lbl, (10 + WIDTH // 3 + 6, HEIGHT - 24))
    else:
        lbl = font_sm.render("Z = Air Blast  ready", True, C_WIND_GLOW)
        surface.blit(lbl, (10, HEIGHT - 24))

    # Zone name flash on entry
    if zone_timer > 0:
        alpha = min(255, zone_timer * 4) if zone_timer > 130 else int(255 * (zone_timer / 130))
        name_surf = font.render(ZONE_NAMES[zone], True, C_WHITE)
        name_surf.set_alpha(alpha)
        surface.blit(name_surf, name_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))


# ── Screens ────────────────────────────────────────────────────────────────────

def draw_start(surface, font_big, font_sm, board: list):
    surface.fill((28, 55, 120))
    rows = [
        (font_big, "AIRBENDER SPIRES",                              C_WHITE),
        (font_sm,  "",                                              C_WHITE),
        (font_sm,  "Climb the Air Temples. Survive Fire Nation.",   C_WHITE),
        (font_sm,  "",                                              C_WHITE),
        (font_sm,  "Move    Arrows / WASD",                         C_WHITE),
        (font_sm,  "Jump    SPACE  (press again mid-air = double)", C_WHITE),
        (font_sm,  "Glide   hold SPACE while falling",              C_WHITE),
        (font_sm,  "Scooter X / Shift  (on ground)",                C_WHITE),
        (font_sm,  "Air Blast   Z / Q  — stuns & kills enemies",    C_WIND_GLOW),
        (font_sm,  "Stomp   land on enemy head to kill",            C_GOLD),
    ]
    if board:
        rows += [(font_sm, "", C_WHITE),
                 (font_sm, f"Best:  {board[0]['name']}  {board[0]['score']:,}", C_GOLD)]
    rows += [(font_sm, "", C_WHITE), (font_sm, "Press any key to start", C_GOLD)]

    for i, (fnt, text, color) in enumerate(rows):
        if text:
            s = fnt.render(text, True, color)
            surface.blit(s, s.get_rect(center=(WIDTH // 2, 85 + i * 44)))


def draw_name_entry(surface, font_big, font_sm, score: int, name: str, blink: bool):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((18, 18, 38, 215))
    surface.blit(ov, (0, 0))
    rows = [
        (font_big, "GAME OVER",           (255, 75, 75)),
        (font_sm,  f"Score:  {score:,}",  C_GOLD),
        (font_sm,  "",                    C_WHITE),
        (font_sm,  "Enter your name:",    C_WHITE),
        (font_big, name + ("|" if blink else " "), C_WHITE),
        (font_sm,  "Press Enter to save", C_WHITE),
    ]
    for i, (fnt, text, color) in enumerate(rows):
        if text:
            s = fnt.render(text, True, color)
            surface.blit(s, s.get_rect(center=(WIDTH // 2, 210 + i * 58)))


def draw_leaderboard(surface, font_big, font_sm, board: list, highlight: str):
    surface.fill(C_DARK)
    surface.blit(font_big.render("LEADERBOARD", True, C_GOLD),
                 font_big.render("LEADERBOARD", True, C_GOLD)
                 .get_rect(center=(WIDTH // 2, 55)))
    for rank, entry in enumerate(board, 1):
        name  = entry["name"]
        pts   = entry["score"]
        color = C_GOLD if name == highlight else C_WHITE
        line  = font_sm.render(f"#{rank:<2}  {name:<12} {pts:>8,}", True, color)
        surface.blit(line, line.get_rect(center=(WIDTH // 2, 110 + rank * 44)))
    footer = font_sm.render("R = play again     Esc = title", True, C_WHITE)
    surface.blit(footer, footer.get_rect(center=(WIDTH // 2, HEIGHT - 30)))


# ── Factory ────────────────────────────────────────────────────────────────────

def make_game():
    level  = ProceduralLevel()
    player = Player(PLAYER_START_X, PLAYER_START_Y)
    cam_y  = float(PLAYER_START_Y - HEIGHT * 0.60)
    return level, player, cam_y


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
    level, player, cam_y = make_game()

    score        = 0
    scroll_count = 0
    final_score  = 0
    name_input   = ""
    last_name    = ""
    blink_timer  = 0
    zone         = 0
    prev_zone    = 0
    zone_timer   = 0   # frames remaining for zone-name display

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
                    level, player, cam_y = make_game()
                    score = scroll_count = 0
                    zone = prev_zone = 0
                    zone_timer = 0
                    state = "play"

        # ── PLAY ───────────────────────────────────────────────────────────────
        elif state == "play":
            # Zone detection
            zone = current_zone(player.rect.y)
            if zone != prev_zone:
                zone_timer = 200
                prev_zone  = zone

            if zone_timer > 0:
                zone_timer -= 1

            # Player input & movement
            player.handle_input(events, keys)
            blast_rect = player.get_blast_rect()

            # Level update — returns (kills, damage, stomp_bounce)
            kills, damage, stomp = level.update(cam_y, player.rect, blast_rect)

            player.update(
                level.solid_platforms(),
                level.wind_currents,
                level.bisons,
            )

            if stomp:
                player.stomp_bounce()

            for _ in range(damage):
                player.take_damage()

            # Collect scrolls
            new_scrolls  = level.check_collect(player.rect)
            scroll_count += new_scrolls

            # Score
            height_gained = max(0, PLAYER_START_Y - player.rect.y)
            score = (int(height_gained / HEIGHT_DIVISOR)
                     + scroll_count * SCROLL_POINTS
                     + kills * KILL_POINTS)

            # Camera — follow player (no auto-scroll)
            target = player.rect.centery - HEIGHT * 0.55
            target = max(0.0, float(target))
            cam_y += (target - cam_y) * CAM_LERP

            # Render
            draw_sky(screen, cam_y, zone)
            bg.draw(screen, cam_y, zone)
            level.draw(screen, cam_y)
            player.draw(screen, cam_y)
            draw_hud(screen, font_big, font_sm, score, scroll_count,
                     player.health, player.blast_cd, zone, zone_timer)

            if player.dead:
                final_score = score
                name_input  = ""
                blink_timer = 0
                state       = "name_entry"

        # ── NAME ENTRY ─────────────────────────────────────────────────────────
        elif state == "name_entry":
            blink_timer += 1
            blink = (blink_timer // 30) % 2 == 0
            draw_sky(screen, cam_y, zone)
            bg.draw(screen, cam_y, zone)
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
                        level, player, cam_y = make_game()
                        score = scroll_count = 0
                        zone = prev_zone = 0
                        zone_timer = 0
                        state = "play"
                    elif ev.key == pygame.K_ESCAPE:
                        state = "start"

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
