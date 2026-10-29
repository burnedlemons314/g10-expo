import math
import random
import sys
import time
from tkinter import *
from tkinter import ttk
import turtle

# ------------------------------------------------------------------ colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED_GIANT = (255, 90, 40)
WHITE_HOT = (210, 230, 255)
ORANGE = (255, 120, 40)


def lerp(a, b, f):
    return a + (b - a) * f


def mix(c1, c2, f):
    """Blend two RGB tuples (0-255); f is clamped to 0..1."""
    f = max(0.0, min(1.0, f))
    return tuple(lerp(c1[i], c2[i], f) for i in range(3))


def col(c):
    if isinstance(c, str):
        return c
    r, g, b = (max(0, min(255, int(v))) for v in c)
    return f"#{r:02x}{g:02x}{b:02x}"


# -------------------------------------------------------------------- setup
screen = None
t = bg = cap = None
CAPTION = ["", ""]
root = Tk()
root.title("Schwarzchild Black Hole Calculator Controller")
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

mfield = StringVar()
mfieldEntry = ttk.Entry(mainframe, width=60, textvariable=mfield)
mfieldEntry.grid(column=2, row = 1, columnspan=4, sticky=(W, E))
mlabel = ttk.Label(mainframe, text = "Enter the initial stellar mass in solar masses")
mlabel.grid(row = 1,sticky=(W, E))

cfield = StringVar()
cfieldEntry = ttk.Entry(mainframe, width=60, textvariable=cfield)
cfieldEntry.grid(column=2, row = 2, columnspan=4, sticky=(W, E))
clabel = ttk.Label(mainframe, text = "Enter the core remnant mass in solar masses")
clabel.grid(row=2, sticky=(W, E))

bfield = StringVar()
bfieldEntry = ttk.Entry(mainframe, width=60, textvariable=bfield)
bfieldEntry.grid(column=2, row = 3, columnspan=4, sticky=(W, E))
blabel = ttk.Label(mainframe, text = "Enter the black hole mass (if applicable) in solar masses")
blabel.grid(row = 3,sticky=(W, E))





def setup():
    global screen, t, bg, cap
    if screen is not None:
        return
    screen = turtle.Screen()
    screen.setup(800, 800)
    screen.bgcolor("black")
    screen.title("Black Hole Calculator")
    screen.tracer(0)  # we redraw manually once per frame
    t = turtle.Turtle()  # main pen, cleared every frame
    cap = turtle.Turtle()  # captions
    for pen in (t, cap):
        pen.hideturtle()
        pen.penup()


def draw_caption():
    cap.clear()
    cap.color("#e8e8e8")
    cap.goto(0, 345)
    cap.write(CAPTION[0], align="center", font=("Arial", 18, "bold"))
    if CAPTION[1]:
        cap.color("#b0b0b0")
        cap.goto(0, -365)
        cap.write(CAPTION[1], align="center", font=("Arial", 14, "normal"))


def tick(delay=0.02):
    draw_caption()
    screen.update()
    if delay:
        time.sleep(delay)


def new_scene(title, subtitle=""):
    screen.bgcolor(0,0,0)
    t.clear()
    t.pensize(1)
    CAPTION[0], CAPTION[1] = title, subtitle
    tick(0)


def circle_at(x, y, r, color, fill=True, width=1, rim=None):
    r = max(r, 0.5)
    t.pensize(width)
    t.goto(x, y - r)
    if rim:
        t.color(col(rim), col(color))
    else:
        t.color(col(color))
    if fill:
        t.begin_fill()
    t.pendown()
    t.circle(r)
    t.penup()
    if fill:
        t.end_fill()


def draw_star(radius, color, glow=ORANGE, layers=4):
    for i in range(layers, 0, -1):
        circle_at(0, 0, radius + i * 8, mix(BLACK, glow, 0.08 * (layers + 1 - i)))
    circle_at(0, 0, radius, color)


# ------------------------------------------------------------ shared effects
def collapse(frames=150, start=220, end=6, c_from=RED_GIANT, c_to=WHITE_HOT, glow=ORANGE):
    """Core collapse: slow start, accelerating, with early-stage instability."""
    for k in range(frames):
        f = k / (frames - 1)
        r = lerp(start, end, f ** 2.2) + math.sin(k * 0.8) * (1 - f) * 6
        t.clear()
        draw_star(max(r, 2), mix(c_from, c_to, f), glow)
        tick()


def flash(n=6, delay=0.05):
    for i in range(n):
        t.clear()
        screen.bgcolor("white" if i % 2 == 0 else "black")
        tick(delay)
    screen.bgcolor("black")


def explosion(frames=80, max_r=430, fireball=0.0, debris=60, ring_end=(255, 80, 20)):
    """Expanding shock ring, optional fireball, and debris flying at different speeds."""
    parts = [(random.uniform(0, 2 * math.pi), random.uniform(0.3, 1.0), random.choice([2, 3, 3, 4]))
             for _ in range(debris)]
    for k in range(frames):
        f = k / (frames - 1)
        r = lerp(10, max_r, f ** 0.7)
        t.clear()
        if fireball and f < 0.85:
            heat = mix(mix(WHITE, ORANGE, f * 2.5), BLACK, f / 0.85)
            circle_at(0, 0, r * fireball, heat)
        circle_at(0, 0, r, mix(WHITE, ring_end, f), fill=False, width=max(1, int(8 * (1 - f))))
        for a, spd, size in parts:
            d = r * spd
            t.goto(math.cos(a) * d, math.sin(a) * d)
            t.dot(size, col(mix((255, 220, 150), (120, 20, 0), f)))
        tick()
    t.pensize(1)


# -------------------------------------------------------------- black hole
TILT = math.radians(-12)
SQUASH = 0.28  # flattens the disk so it looks tilted
INNER, OUTER = 1.6, 4.2


def make_disk(n=320):
    return [[random.uniform(0, 2 * math.pi), random.uniform(INNER, OUTER),
             random.choice([1, 2, 2, 3])] for _ in range(n)]


def disk_point(angle, dist, horizon):
    x = math.cos(angle) * dist * horizon
    y = math.sin(angle) * dist * horizon * SQUASH
    return (x * math.cos(TILT) - y * math.sin(TILT),
            x * math.sin(TILT) + y * math.cos(TILT))


def disk_color(dist):
    return mix((255, 255, 235), (190, 45, 15), (dist - INNER) / (OUTER - INNER))


def draw_disk_half(particles, horizon, front):
    for angle, dist, size in particles:
        if (math.sin(angle) < 0) != front:
            continue
        x, y = disk_point(angle, dist, horizon)
        t.goto(x, y)
        t.dot(size, col(disk_color(dist)))


def draw_black_hole(particles, horizon):
    t.clear()
    draw_disk_half(particles, horizon, front=False)  # back of the disk
    circle_at(0, 0, horizon, BLACK, width=3, rim="#ff9a3c")  # event horizon
    t.pensize(2)  # lensing arc
    t.color("#ffcf8a")
    t.goto(horizon * 1.3, 0)
    t.setheading(90)
    t.pendown()
    t.circle(horizon * 1.3, 180)
    t.penup()
    t.setheading(0)
    t.pensize(1)
    draw_disk_half(particles, horizon, front=True)  # front of the disk


def horizon_for_mass(M):
    """On-screen horizon radius. Log-scaled, so it is NOT to scale with the real radius."""
    return min(70, 24 + 14 * math.log10(max(M, 1)))


def show_black_hole(M, sr, grow=60, hold=300):
    target = horizon_for_mass(M)
    CAPTION[1] = f"Schwarzschild radius: {sr:,.2f} km   (M = {M:g} solar masses)"
    particles = make_disk()
    for k in range(grow + hold):
        h = lerp(4, target, (k / (grow - 1)) ** 0.6) if k < grow else target
        for p in particles:
            p[0] += 0.28 / p[1] ** 1.5  # inner particles orbit faster
        draw_black_hole(particles, h)
        tick()


# ------------------------------------------------------------ neutron star
def pulsar(hold=300):
    for k in range(hold):
        a = k * 0.18
        t.clear()
        for i in range(3, 0, -1):
            circle_at(0, 0, 6 + i * 6, mix(BLACK, (80, 120, 255), 0.10 * (4 - i)))
        for side in (0, math.pi):
            ex, ey = math.cos(a + side) * 330, math.sin(a + side) * 330
            for w, f in ((9, 0.12), (5, 0.3), (2, 0.9)):
                t.pensize(w)
                t.color(col(mix(BLACK, (190, 220, 255), f)))
                t.goto(0, 0)
                t.pendown()
                t.goto(ex, ey)
                t.penup()
        t.pensize(1)
        circle_at(0, 0, 6, (220, 235, 255))
        tick()


# -------------------------------------------------------------- white dwarf
def scene_white_dwarf():
    new_scene("Low-mass star: planetary nebula and white dwarf",
              "Not enough mass for a supernova or a black hole")
    for k in range(80):  # swells into a red giant
        f = k / 79
        t.clear()
        draw_star(lerp(70, 210, f ** 1.5), mix((255, 220, 90), (255, 70, 30), f), glow=(255, 110, 30))
        tick()
    shells = [(0, (90, 230, 190)), (14, (230, 120, 200)), (28, (90, 230, 190)),
              (42, (230, 120, 200)), (56, (120, 200, 255))]
    total = 220
    for k in range(total):  # shells puff off, core shrinks
        t.clear()
        cf = min(1.0, k / 60)
        for delay, color in shells:
            if k < delay:
                continue
            f = (k - delay) / (total - delay)
            circle_at(0, 0, 210 + (k - delay) * 1.5, mix(color, BLACK, f), fill=False, width=4)
        draw_star(lerp(210, 7, cf ** 0.5), mix(RED_GIANT, WHITE_HOT, cf),
                  glow=mix(ORANGE, (120, 150, 255), cf), layers=2)
        tick()
    for k in range(90):  # the white dwarf cools quietly
        t.clear()
        draw_star(7 + math.sin(k * 0.3), WHITE_HOT, glow=(120, 150, 255), layers=2)
        tick()


# --------------------------------------------------------------- the scenes
def scene_direct_collapse(M, sr):
    new_scene("Photodisintegration: direct collapse, no nova",
              "The star falls straight into a black hole without exploding")
    collapse(frames=150, start=230, end=10, c_to=(90, 20, 10), glow=(110, 30, 10))
    for k in range(40):  # the last light is swallowed
        f = k / 39
        t.clear()
        circle_at(0, 0, lerp(10, 5, f), mix((90, 20, 10), BLACK, f))
        tick()
    show_black_hole(M, sr)


def scene_pisn():
    new_scene("Pair-instability supernova: hypernova, no remnant",
              "The star is torn apart completely and leaves nothing behind")
    r = 160
    for k in range(150):  # violent pulsations
        f = k / 149
        r = 160 + math.sin(k * 0.22) * (8 + 60 * f)
        t.clear()
        draw_star(r, mix(RED_GIANT, WHITE_HOT, f), glow=(255, 160, 60))
        tick()
    for k in range(30):  # final runaway contraction
        r2 = lerp(r, 30, (k / 29) ** 2)
        t.clear()
        draw_star(r2, WHITE_HOT, glow=(255, 200, 120))
        tick()
    flash(10, 0.04)
    explosion(frames=140, max_r=650, fireball=0.9, debris=160)
    t.clear()  # nothing remains
    for _ in range(80):
        tick()


def scene_core_collapse_bh(M, sr):
    new_scene("Core collapse: supernova leaves a black hole")
    collapse()
    flash()
    explosion(fireball=0.5)
    show_black_hole(M, sr)


def scene_neutron_star(title="Core too light for a black hole: neutron star",
                       subtitle="Core mass is not enough, so the collapse halts as a neutron star"):
    new_scene(title, subtitle)
    collapse()
    flash()
    explosion(fireball=0.5)
    pulsar()


def scene_low_mass(m):
    if m < 8:
        scene_white_dwarf()
    else:
        scene_neutron_star("Star too light for a black hole: neutron star",
                           "Mass of the star is not enough for a black hole")



def scene_message(title, text, hold=120):
    new_scene(title)
    t.goto(0, -10)
    t.color("#ff6b6b")
    t.write(text, align="center", font=("Arial", 22, "bold"))
    for _ in range(hold):
        tick()

def black_hole():
    M = float(bfield.get())
    sr = 2.95325 * M
    print("Schwarzschild Radius:", sr, "km")
    return M, sr

# ------------------------------------------------------------- calculator
def run_calculator():

    mvar = mfield.get()
    cvar = cfield.get()

    print(mvar,cvar)

    if mvar == "demo":
        run_demo()
        return

    m = float(mvar)
    c = float(cvar)


    if m <= 0 or c < 0 or c > m:
        print("Invalid mass values.")
        setup()
        scene_message("Invalid input", "Invalid mass values.")
        return


    if m >= 260:
        if c > 2:
            outcome = "direct"
            print("The star undergoes photodisintegration and leaves only a Black Hole behind, but no nova")
        else:
            outcome = "core_small"
            print("Core mass is not enough")
    elif m >= 130:
        if c > 2:
            outcome = "pisn"
            print(" The star is too heavy but also too light. Goes through PISN(pair-instability "
                  "supernova) and leaves a hypernova and nothing else behind")
        else:
            outcome = "core_small"
            print("Core mass is not enough")
    elif m >= 20:
        if c > 2:
            outcome = "core_bh"
            print("Mass is sufficient for possible black-hole formation after core collapse")
        else:
            outcome = "core_small"
            print("Core mass is not enough")
    else:
        outcome = "low_mass"
        print("Mass of the star is not enough")

    M, sr = black_hole()


    setup()
    if outcome == "direct":
        scene_direct_collapse(M, sr)
    elif outcome == "pisn":
        scene_pisn()
    elif outcome == "core_bh":
        scene_core_collapse_bh(M, sr)
    elif outcome == "core_small":
        scene_neutron_star()
    elif outcome == "low_mass":
        scene_low_mass(m)

    outcome = None

def run_demo():
    global ISDEMO
    ISDEMO = True
    setup()
    scene_direct_collapse(100, 2.95325 * 100)
    scene_pisn()
    scene_core_collapse_bh(8, 2.95325 * 8)
    scene_neutron_star()
    scene_white_dwarf()


calculatebutton = ttk.Button(mainframe, text="Calculate", command=run_calculator)
calculatebutton.grid(column=1, row=4, columnspan=4, sticky=(W, E))

root.mainloop()

