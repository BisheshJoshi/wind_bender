"""
Run once:  python extract_sprites.py
Scans the spritesheet for non-white pixel clusters, saves each as a
numbered PNG in sprites/ and prints a manifest of (x, y, w, h) rects.
"""

import os
import pygame

SHEET = "Game Boy Advance - Avatar_ The Last Airbender - Playable Characters - Avatar Aang.png"
OUT   = "sprites"
BG    = (255, 255, 255)   # colorkey color to treat as transparent
PAD   = 2                 # extra padding around each detected sprite

os.makedirs(OUT, exist_ok=True)

pygame.init()
pygame.display.set_mode((1, 1))   # minimal display required for convert()
sheet = pygame.image.load(SHEET).convert()
W, H  = sheet.get_size()
print(f"Sheet size: {W} x {H}")

# Build a boolean occupancy map: True = non-background pixel
pxa = pygame.PixelArray(sheet)

def is_bg(x, y):
    r, g, b, *_ = sheet.get_at((x, y))
    # allow slight anti-alias fringe
    return r >= 250 and g >= 250 and b >= 250

occ = [[not is_bg(x, y) for x in range(W)] for y in range(H)]

# ── Connected-component labeling (flood fill, iterative) ──────────────────────
label = [[-1] * W for _ in range(H)]
components = []   # list of sets of (x,y)

def flood(sx, sy, comp_id):
    stack = [(sx, sy)]
    comp  = []
    while stack:
        x, y = stack.pop()
        if x < 0 or x >= W or y < 0 or y >= H:
            continue
        if label[y][x] != -1 or not occ[y][x]:
            continue
        label[y][x] = comp_id
        comp.append((x, y))
        stack += [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    return comp

comp_id = 0
for sy in range(H):
    for sx in range(W):
        if occ[sy][sx] and label[sy][sx] == -1:
            comp = flood(sx, sy, comp_id)
            if len(comp) >= 8:          # skip tiny noise pixels
                components.append(comp)
                comp_id += 1

del pxa   # release pixel array

print(f"Found {len(components)} components (sprites/groups)")

# ── Merge nearby small components into sprite bounding boxes ─────────────────
def bbox(comp):
    xs = [p[0] for p in comp]
    ys = [p[1] for p in comp]
    return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1

rects = [bbox(c) for c in components]

# Sort by top-left reading order
rects.sort(key=lambda r: (r[1] // 4, r[0]))

# Merge overlapping/adjacent rects (within 4px of each other)
MERGE_GAP = 4
merged = []
for rx, ry, rw, rh in rects:
    placed = False
    for i, (mx, my, mw, mh) in enumerate(merged):
        if (rx < mx + mw + MERGE_GAP and rx + rw > mx - MERGE_GAP and
                ry < my + mh + MERGE_GAP and ry + rh > my - MERGE_GAP):
            # Union
            nx = min(rx, mx);  ny = min(ry, my)
            merged[i] = (nx, ny,
                         max(rx+rw, mx+mw) - nx,
                         max(ry+rh, my+mh) - ny)
            placed = True
            break
    if not placed:
        merged.append((rx, ry, rw, rh))

# Re-sort after merging
merged.sort(key=lambda r: (r[1] // 6, r[0]))
print(f"After merging: {len(merged)} sprites")

# ── Save each sprite + print manifest ────────────────────────────────────────
manifest = []
for i, (x, y, w, h) in enumerate(merged):
    px = max(0, x - PAD);  py = max(0, y - PAD)
    pw = min(W - px, w + PAD * 2)
    ph = min(H - py, h + PAD * 2)

    sub = sheet.subsurface((px, py, pw, ph)).copy()
    sub.set_colorkey(BG)

    fname = f"{OUT}/sprite_{i:03d}.png"
    pygame.image.save(sub, fname)
    manifest.append((i, px, py, pw, ph))
    if i < 30 or pw * ph > 800:           # print first 30 + large ones
        print(f"  [{i:03d}] x={px:4d} y={py:4d}  {pw:3d}x{ph:3d}  {fname}")

print(f"\nAll {len(merged)} sprites saved to ./{OUT}/")
print("Open sprites/ to identify which number is which animation.")
pygame.quit()
