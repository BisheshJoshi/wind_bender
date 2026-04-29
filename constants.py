WIDTH  = 720
HEIGHT = 900
FPS    = 60
TITLE  = "Airbender Spires"

# Camera
CAM_LERP = 0.10

# Rising death floor
FLOOR_RISE_SPEED = 0.35    # px / frame at start
FLOOR_RISE_MAX   = 1.80    # px / frame ceiling
FLOOR_RISE_ACCEL = 0.00012 # px / frame² acceleration

# Physics
GRAVITY          = 0.55
WALK_SPEED       = 3.5
JUMP_VEL         = -13.5
DOUBLE_JUMP_VEL  = -11.5
GLIDE_GRAVITY    = 0.09
GLIDE_MAX_FALL   = 1.8
SCOOTER_SPEED    = 10.0
SCOOTER_FRAMES   = 45
WIND_BOOST_VEL   = -17.0

# Player health & combat
PLAYER_MAX_HEALTH  = 3
INV_FRAMES         = 90    # invincibility after taking damage
BLAST_RANGE        = 95
BLAST_COOLDOWN     = 45
BLAST_ANIM_FRAMES  = 10

# Enemies
ENEMY_SPEED            = 0.9
ENEMY_FIRE_MIN         = 110   # frames between shots
ENEMY_FIRE_MAX         = 200
FIREBALL_SPEED         = 3.8
KILL_POINTS            = 50

# Scoring
SCROLL_POINTS  = 15
HEIGHT_DIVISOR = 4

# Zone altitude thresholds (units climbed from start)
ZONE_ALTS  = [0, 900, 2200, 3800]
ZONE_NAMES = [
    "Southern Air Temple",
    "Eastern Air Temple",
    "Northern Mountaintop",
    "Spirit World",
]

# Per-zone platform colours  (main, trim, dark, edge, pillar)
ZONE_PLAT = [
    [(155,115, 75), (195,160,105), ( 85, 55, 30), (110, 80, 45), (130, 95, 60)],
    [(100,115, 90), (138,155,118), ( 62, 72, 52), ( 78, 93, 68), ( 88,103, 78)],
    [(172,182,198), (208,218,228), (112,122,138), (142,152,165), (158,168,180)],
    [( 42,148,142), ( 72,192,186), ( 18, 92, 88), ( 32,118,112), ( 52,162,156)],
]

# Per-zone sky: (high-altitude colour, low-altitude colour)
ZONE_SKY = [
    [( 28,  55, 120), (130, 185, 235)],
    [( 18,  42, 110), ( 58, 108, 182)],
    [(152, 168, 192), (198, 212, 232)],
    [( 52,  14,  92), ( 92,  42, 142)],
]

# Player body
C_BODY      = (220, 110,  15)
C_PANTS     = (235, 225, 185)
C_BELT      = (160,  80,  10)
C_HEAD      = (255, 210, 165)
C_ARROW     = ( 80, 150, 255)
C_EYE       = ( 25,  15,   5)
C_GLIDER    = (165, 125,  50)
C_GLIDER2   = (200, 160,  80)
C_SCOOTER   = (255, 210,  35)
C_SCOOTER2  = (255, 240, 120)

# Wind current
C_WIND      = (175, 228, 255)
C_WIND_GLOW = (210, 242, 255)

# Collectible
C_COLLECT   = (255, 215,   0)
C_COLLECT2  = (200, 165,  15)

# Bison
C_BISON     = (245, 245, 242)
C_BISON_OUT = (175, 170, 160)
C_BISON_LEG = (200, 195, 185)

# Enemy
C_ENEMY_ARMOR = (185,  45,  20)
C_ENEMY_HELM  = (115,  28,  10)
C_ENEMY_EYE   = (255, 200,   0)
C_FIREBALL    = (255, 130,  10)
C_FIREBALL2   = (255, 240, 100)

# Spirit World enemy tint
C_SPIRIT_ARMOR = (140,  22, 172)
C_SPIRIT_HELM  = ( 90,  12, 118)

# Background layers
C_CLOUD       = (215, 232, 252)
C_LANTERN     = (255, 155,  35)

# UI
C_WHITE     = (255, 255, 255)
C_DARK      = ( 18,  18,  38)
C_GOLD      = (255, 215,   0)
C_HEALTH_ON = ( 80, 200, 255)
C_HEALTH_OFF= ( 50,  50,  70)

# Starting position
PLAYER_START_X = 360
PLAYER_START_Y = 5100
