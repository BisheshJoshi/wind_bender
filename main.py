import sys
import math
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
    lo = ZONE_ALTS[zone]
    hi = ZONE_ALTS[zone + 1] if zone + 1 < len(ZONE_ALTS) else lo + 1600
    t  = min(1.0, max(0.0, (max(0.0, PLAYER_START_Y - cam_y) - lo) / (hi - lo)))
    r = int(low_col[0] * (1 - t) + high_col[0] * t)
    g = int(low_col[1] * (1 - t) + high_col[1] * t)
    b = int(low_col[2] * (1 - t) + high_col[2] * t)
    surface.fill((r, g, b))


# ── Rising death floor ─────────────────────────────────────────────────────────

_FLOOR_GRAD_H = 90

def _build_floor_gradient() -> pygame.Surface:
    """Pre-bake the smoke/fire gradient drawn above the floor line."""
    surf = pygame.Surface((WIDTH, _FLOOR_GRAD_H), pygame.SRCALPHA)
    for row in range(_FLOOR_GRAD_H):
        a = int(210 * (row / _FLOOR_GRAD_H) ** 1.4)
        pygame.draw.line(surf, (18, 0, 0, a), (0, row), (WIDTH - 1, row))
    return surf


def draw_floor(surface, grad: pygame.Surface, floor_screen_y: int, tick: int):
    """Fire wall that consumes everything below the camera."""
    if floor_screen_y > HEIGHT + _FLOOR_GRAD_H:
        return

    # Smoke / ash gradient rising above the line
    surface.blit(grad, (0, floor_screen_y - _FLOOR_GRAD_H))

    # Solid void below the line
    if floor_screen_y < HEIGHT:
        pygame.draw.rect(surface, (6, 0, 0),
                         (0, floor_screen_y, WIDTH, HEIGHT - floor_screen_y))

    # Fire line itself
    if -4 <= floor_screen_y <= HEIGHT + 4:
        pygame.draw.line(surface, (255,  70,  0),
                         (0, floor_screen_y), (WIDTH, floor_screen_y), 4)
        pygame.draw.line(surface, (255, 200, 50),
                         (0, floor_screen_y - 1), (WIDTH, floor_screen_y - 1), 1)

    # Embers drifting upward
    for i in range(12):
        age = (tick * 2 + i * 29) % 85
        sx  = (i * 59 + tick * 7) % WIDTH
        sy  = floor_screen_y - age
        if 0 <= sy <= HEIGHT:
            t = 1.0 - age / 85
            pygame.draw.circle(surface, (255, int(110 * t), 0),
                               (sx, sy), max(1, int(3 * t)))

    # Pulsing danger border when floor is on-screen
    if floor_screen_y < HEIGHT + 10:
        pulse = abs(math.sin(tick * 0.09))
        warn  = pygame.Surface((WIDTH, 10), pygame.SRCALPHA)
        warn.fill((255, 40, 0, int(140 * pulse)))
        surface.blit(warn, (0, HEIGHT - 10))


# ── HUD ────────────────────────────────────────────────────────────────────────

def draw_hud(surface, font, font_sm, score: int, scroll_count: int,
             health: int, blast_cd: int, zone: int, zone_timer: int,
             floor_screen_y: int):
    # Chi health orbs
    for i in range(PLAYER_MAX_HEALTH):
        col = C_HEALTH_ON if i < health else C_HEALTH_OFF
        cx  = 18 + i * 26
        pygame.draw.circle(surface, col,   (cx, 18), 10)
        pygame.draw.circle(surface, C_WHITE, (cx, 18), 10, 1)
        pygame.draw.circle(surface, C_WHITE if i < health else C_DARK, (cx, 18), 4)

    surface.blit(font.render(f"{score:,}", True, C_WHITE), (10, 38))
    surface.blit(font_sm.render(f"Scrolls  {scroll_count}", True, C_GOLD), (10, 62))

    # Blast cooldown
    if blast_cd > 0:
        bw = int((WIDTH // 3) * (1 - blast_cd / BLAST_COOLDOWN))
        pygame.draw.rect(surface, C_WIND_GLOW, (10, HEIGHT - 22, bw, 8))
        pygame.draw.rect(surface, C_WHITE,     (10, HEIGHT - 22, WIDTH // 3, 8), 1)
        surface.blit(font_sm.render("blast", True, C_WHITE),
                     (10 + WIDTH // 3 + 6, HEIGHT - 24))
    else:
        surface.blit(font_sm.render("Z = Air Blast  ready", True, C_WIND_GLOW),
                     (10, HEIGHT - 24))

    # Zone name flash on entry
    if zone_timer > 0:
        a = min(255, zone_timer * 4) if zone_timer > 130 else int(255 * zone_timer / 130)
        ns = font.render(ZONE_NAMES[zone], True, C_WHITE)
        ns.set_alpha(a)
        surface.blit(ns, ns.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

    # Floor warning label when it's close
    if floor_screen_y < HEIGHT - 60:
        warn_surf = font_sm.render("▼  FLOOR RISING  ▼", True, (255, 100, 20))
        surface.blit(warn_surf, warn_surf.get_rect(centerx=WIDTH // 2,
                                                    bottom=floor_screen_y - 6))


# ── Screens ────────────────────────────────────────────────────────────────────

def draw_start(surface, font_big, font_sm, board: list):
    surface.fill((28, 55, 120))
    rows = [
        (font_big, "AIRBENDER SPIRES",                              C_WHITE),
        (font_sm,  "",                                              C_WHITE),
        (font_sm,  "Climb the Air Temples. Survive Fire Nation.",   C_WHITE),
        (font_sm,  "The floor is rising — don't fall behind.",      (255, 130, 40)),
        (font_sm,  "",                                              C_WHITE),
        (font_sm,  "Move    Arrows / WASD",                         C_WHITE),
        (font_sm,  "Jump    SPACE  (press again mid-air = double)", C_WHITE),
        (font_sm,  "Glide   hold SPACE while falling",              C_WHITE),
        (font_sm,  "Scooter X / Shift  (on ground)",                C_WHITE),
        (font_sm,  "Air Blast   Z / Q  — kills enemies",            C_WIND_GLOW),
        (font_sm,  "Stomp   land on enemy head",                    C_GOLD),
    ]
    if board:
        rows += [(font_sm, "", C_WHITE),
                 (font_sm, f"Best:  {board[0]['name']}  {board[0]['score']:,}", C_GOLD)]
    rows += [(font_sm, "", C_WHITE), (font_sm, "Press any key to start", C_GOLD)]
    for i, (fnt, text, color) in enumerate(rows):
        if text:
            s = fnt.render(text, True, color)
            surface.blit(s, s.get_rect(center=(WIDTH // 2, 75 + i * 42)))


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
        color = C_GOLD if entry["name"] == highlight else C_WHITE
        line  = font_sm.render(
            f"#{rank:<2}  {entry['name']:<12} {entry['score']:>8,}", True, color)
        surface.blit(line, line.get_rect(center=(WIDTH // 2, 110 + rank * 44)))
    surface.blit(font_sm.render("R = play again     Esc = title", True, C_WHITE),
                 font_sm.render("R = play again     Esc = title", True, C_WHITE)
                 .get_rect(center=(WIDTH // 2, HEIGHT - 30)))


# ── Factory ────────────────────────────────────────────────────────────────────

def make_game():
    level   = ProceduralLevel()
    player  = Player(PLAYER_START_X, PLAYER_START_Y)
    cam_y   = float(PLAYER_START_Y - HEIGHT * 0.60)

    # Camera ratchet: tracks the highest (min Y) the camera has ever reached.
    # Once set, the camera can never scroll back down.
    cam_floor = cam_y

    # Death floor starts below the visible screen so the player isn't
    # immediately threatened; rises from there at FLOOR_RISE_SPEED.
    death_floor_y = float(cam_y + HEIGHT + 250)
    floor_spd     = FLOOR_RISE_SPEED

    return level, player, cam_y, cam_floor, death_floor_y, floor_spd


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.mixer.pre_init(22050, -16, 2, 512)
    pygame.init()
    screen   = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption(TITLE)
    clock    = pygame.time.Clock()
    font_big = pygame.font.SysFont("Arial", 36, bold=True)
    font_sm  = pygame.font.SysFont("Arial", 17)

    try:
        pygame.mixer.music.load("Light battle.ogg")
        pygame.mixer.music.set_volume(0.55)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    bg           = Background()
    board        = scoreboard.load()
    floor_grad   = _build_floor_gradient()

    state = "start"
    level, player, cam_y, cam_floor, death_floor_y, floor_spd = make_game()

    score        = 0
    scroll_count = 0
    final_score  = 0
    name_input   = ""
    last_name    = ""
    blink_timer  = 0
    zone         = 0
    prev_zone    = 0
    zone_timer   = 0
    game_tick    = 0

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
                    level, player, cam_y, cam_floor, death_floor_y, floor_spd = make_game()
                    score = scroll_count = game_tick = 0
                    zone = prev_zone = zone_timer = 0
                    state = "play"

        # ── PLAY ───────────────────────────────────────────────────────────────
        elif state == "play":
            game_tick += 1

            # ── Zone detection ────────────────────────────────────────────────
            zone = current_zone(player.rect.y)
            if zone != prev_zone:
                zone_timer = 200
                prev_zone  = zone
            if zone_timer > 0:
                zone_timer -= 1

            # ── Rising death floor ────────────────────────────────────────────
            floor_spd     = min(FLOOR_RISE_MAX, floor_spd + FLOOR_RISE_ACCEL)
            death_floor_y -= floor_spd

            # Ratchet: floor locks to camera bottom if camera overtook it
            death_floor_y = min(death_floor_y, cam_floor + HEIGHT)

            # ── Input & physics ───────────────────────────────────────────────
            for ev in events:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    state = "start"
            player.handle_input(events, keys)
            blast_rect = player.get_blast_rect()

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

            scroll_count += level.check_collect(player.rect)

            # ── Camera ────────────────────────────────────────────────────────
            target    = player.rect.centery - HEIGHT * 0.55
            cam_y    += (target - cam_y) * CAM_LERP

            # Ratchet: camera never scrolls back down
            cam_floor = min(cam_floor, cam_y)
            cam_y     = min(cam_y, cam_floor)

            # ── Death check ───────────────────────────────────────────────────
            if player.rect.bottom > death_floor_y or player.dead:
                player.dead = True

            # ── Score ─────────────────────────────────────────────────────────
            height_gained = max(0, PLAYER_START_Y - player.rect.y)
            score = (int(height_gained / HEIGHT_DIVISOR)
                     + scroll_count * SCROLL_POINTS
                     + kills * KILL_POINTS)

            # ── Render ────────────────────────────────────────────────────────
            floor_screen_y = int(death_floor_y - cam_y)

            draw_sky(screen, cam_y, zone)
            bg.draw(screen, cam_y, zone)
            level.draw(screen, cam_y)
            player.draw(screen, cam_y)
            draw_floor(screen, floor_grad, floor_screen_y, game_tick)
            draw_hud(screen, font_big, font_sm, score, scroll_count,
                     player.health, player.blast_cd, zone, zone_timer,
                     floor_screen_y)

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
            draw_floor(screen, floor_grad, int(death_floor_y - cam_y), game_tick)
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
                        level, player, cam_y, cam_floor, death_floor_y, floor_spd = make_game()
                        score = scroll_count = game_tick = 0
                        zone = prev_zone = zone_timer = 0
                        state = "play"
                    elif ev.key == pygame.K_ESCAPE:
                        state = "start"

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
