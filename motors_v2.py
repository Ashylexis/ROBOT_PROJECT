from machine import Pin
import time
import math

# ============================================================
#  Raspberry Pi Pico + 2x DRV8825
#  M0, M1, M2 câblés HIGH en dur → 1/32 microstepping
# ============================================================

# --- Broches (GPIO) ---
R_STEP = Pin(19, Pin.OUT)
R_DIR  = Pin(20, Pin.OUT)
L_STEP = Pin(26, Pin.OUT)
L_DIR  = Pin(18, Pin.OUT)
# EN actif LOW : 0 = driver actif, 1 = driver désactivé (silencieux)
# Relier EN du driver droit à GPIO 21, gauche à GPIO 27
# Si vous ne voulez pas câbler EN, mettre USE_ENABLE = False
USE_ENABLE = False
R_EN = Pin(21, Pin.OUT) if USE_ENABLE else None
L_EN = Pin(27, Pin.OUT) if USE_ENABLE else None

# --- Mécanique (à ajuster selon votre robot) ---
WHEEL_DIAM_MM = 68.0
WHEELBASE_MM  = 180.0
STEPS_PER_REV = 200 * 32              # 1/32 microstepping → 6400 pas/tour
WHEEL_CIRC_MM = math.pi * WHEEL_DIAM_MM

# Moteurs montés en miroir → un côté inversé
L_INVERT = False
R_INVERT = True

# Chaque pas moteur = 1 impulsion électrique (STEP) + 1 temps d'attente (DELAY).
# La rampe accélère en vitesse (pas/s) de façon linéaire : le robot ressent une montée en vitesse régulière et constante.

PULSE_US    = 2     # Durée fixe de chaque impulsion STEP en µs. Imposée par le composant DRV8825, ne pas modifier.
SPEED_START = 500   # Vitesse de départ en pas/s. Baisser si le moteur cale au démarrage.
SPEED_MAX   = 3000  # Vitesse de croisière en pas/s. Augmenter pour aller plus vite.


# ============================================================
#  MOTEUR BAS NIVEAU
# ============================================================

def _enable(on):
    if USE_ENABLE:
        R_EN.value(0 if on else 1)   # EN actif LOW
        L_EN.value(0 if on else 1)


def _set_dir(fwd_l, fwd_r):
    L_DIR.value(1 if (fwd_l != L_INVERT) else 0)
    R_DIR.value(1 if (fwd_r != R_INVERT) else 0)
    time.sleep_us(50)   # setup time DIR→STEP exigé par DRV8825


def _move(n, fwd_l, fwd_r):
    """Déplace les 2 moteurs de n micropas avec rampe acc/déc linéaire en vitesse."""
    _enable(True)
    _set_dir(fwd_l, fwd_r)

    half = n // 2

    for i in range(n):
        L_STEP.value(1); R_STEP.value(1)
        time.sleep_us(PULSE_US)
        L_STEP.value(0); R_STEP.value(0)

        # Vitesse augmente linéairement pendant la 1ère moitié
        # puis redescend linéairement pendant la 2ème moitié
        if i < half:
            vitesse = SPEED_START + (SPEED_MAX - SPEED_START) * i // half
        else:
            vitesse = SPEED_START + (SPEED_MAX - SPEED_START) * (n - i) // half

        time.sleep_us(1_000_000 // vitesse)

    _enable(False)   # coupe le courant → silence au repos


def _mm_to_steps(mm):
    return max(1, int(abs(mm) / WHEEL_CIRC_MM * STEPS_PER_REV))


# ============================================================
#  API MOUVEMENT
# ============================================================

def avancer(mm):
    """Avance droit de mm millimètres."""
    _move(_mm_to_steps(mm), True, True)

def reculer(mm):
    """Recule droit de mm millimètres."""
    _move(_mm_to_steps(mm), False, False)

def tourner(deg):
    """Tourne sur place. Positif = droite, négatif = gauche."""
    arc_mm = (WHEELBASE_MM / 2) * abs(deg) * math.pi / 180
    n = _mm_to_steps(arc_mm)
    if deg >= 0:
        _move(n, True,  False)   # L avant, R arrière → tourne à droite
    else:
        _move(n, False, True)    # L arrière, R avant → tourne à gauche


# ============================================================
#  FONCTIONS DE DIAGNOSTIC
#  Utiliser en priorité si les moteurs ne tournent pas correctement
# ============================================================

def test_un_moteur(step_pin, dir_pin, invert, n_tours=1, delay_us=10000, fwd=True):
    """
    Tourne UN seul moteur, très lentement, sans accélération.
    Permet de vérifier le câblage et de trouver le delay minimum viable.
    """
    dir_pin.value(1 if (fwd != invert) else 0)
    time.sleep_us(50)
    total = STEPS_PER_REV * n_tours
    for _ in range(total):
        step_pin.value(1)
        time.sleep_us(PULSE_US)
        step_pin.value(0)
        time.sleep_us(delay_us)


def calibrer_delay(step_pin, dir_pin, invert, delay_start=20000, step_dec=500):
    """
    Cherche le delay minimum : démarre très lentement, accélère par
    paliers de step_dec µs jusqu'à ce que le moteur décroche.
    Observer et noter le delay auquel ça commence à vibrer.
    """
    dir_pin.value(1 if (True != invert) else 0)
    time.sleep_us(50)
    d = delay_start
    print("Calibration — delay en µs (Ctrl+C pour arrêter) :")
    while d >= 200:
        print("  delay = {}µs  ({} pas/s)".format(d, 1_000_000 // d))
        for _ in range(STEPS_PER_REV // 4):   # 1/4 de tour par palier
            step_pin.value(1)
            time.sleep_us(PULSE_US)
            step_pin.value(0)
            time.sleep_us(d)
        d -= step_dec
        time.sleep_ms(200)


# ============================================================
#  GÉOMÉTRIE DU PLATEAU  (toutes valeurs en mm)
# ============================================================
#
#  Table 2000 × 900 mm, vue de dessus :
#
#   0mm ┌──────────────────────────────────────┐
#       │[ROUGE 250×250]         [château ●●]  │
#       │                                      │
#  950mm│══════════════[RIVIÈRE 100mm]══════════│
# 1050mm│══════════════════════════════════════│
#       │                                      │
#       │[château ●●]        [VERT 250×250]    │
# 2000mm└──────────────────────────────────────┘
#        0mm                             900mm
#
#  Robot dans la zone ROUGE, face au château haut-droite → face à DROITE
#  Après 90° droite → face vers le BAS (sens des 2000mm)
#  Le robot (24.5mm dans le sens 2000mm) est centré dans la zone → 125mm du bord haut
#  Front du robot après virage = 125 + 24.5/2 = 137mm depuis le haut
#  Bord proche de la rivière   = 1000 - 100/2  = 950mm depuis le haut
#  Distance à parcourir        = 950 - 137      = 813mm
#
#  ↓ Ajuster si le robot n'est pas centré dans sa zone de départ
ROBOT_PROF_MM    = 24.5    # dimension robot dans le sens 2000mm
ZONE_DEPART_MM   = 250     # côté de la zone de départ
RIVIERE_CENTRE   = 1000    # centre rivière depuis le bord haut
RIVIERE_LARG_MM  = 100     # largeur rivière (10 cm)

_y_robot = ZONE_DEPART_MM / 2 + ROBOT_PROF_MM / 2   # avant du robot depuis le haut
_y_river = RIVIERE_CENTRE - RIVIERE_LARG_MM / 2      # bord proche rivière depuis le haut
DISTANCE_RIVIERE_MM = int(_y_river - _y_robot)       # = 813 mm

PAUSE_MS = 300   # pause entre les actions (ms)


def mission():
    print("=== MISSION DÉMARRÉE ===")
    print("Zone départ → rivière : {} mm calculés".format(DISTANCE_RIVIERE_MM))

    print("1. Virage 90° droite...")
    tourner(90)
    time.sleep_ms(PAUSE_MS)

    print("2. Avance vers la rivière ({} mm)...".format(DISTANCE_RIVIERE_MM))
    avancer(DISTANCE_RIVIERE_MM)

    print("=== RIVIÈRE ATTEINTE — ARRÊT ===")


# ============================================================
#  DÉMARRAGE
#  - Batterie seule      : mission lance après le compte à rebours
#  - Branché à Thonny    : appuyer Ctrl+C → mode interactif
# ============================================================
L_STEP.value(0); R_STEP.value(0)

DELAI_DEPART_S = 5

print("╔══════════════════════════════════════╗")
print("║       ROBOT — GUERRE DES TRÔNES     ║")
print("╠══════════════════════════════════════╣")
print("║  Ctrl+C → mode interactif            ║")
print("╚══════════════════════════════════════╝")

try:
    for i in range(DELAI_DEPART_S, 0, -1):
        print("  Départ dans {}s...".format(i))
        time.sleep(1)
    mission()

except KeyboardInterrupt:
    print()
    print("Mode interactif — commandes disponibles :")
    print("  avancer(mm)              ex: avancer(200)")
    print("  reculer(mm)              ex: reculer(100)")
    print("  tourner(deg)             ex: tourner(90)  ou tourner(-45)")
    print("  test_un_moteur(R_STEP, R_DIR, R_INVERT)   moteur droit seul")
    print("  test_un_moteur(L_STEP, L_DIR, L_INVERT)   moteur gauche seul")
    print("  calibrer_delay(R_STEP, R_DIR, R_INVERT)   cherche le delay min")
    print("  mission()                lance le parcours complet")
