import tkinter as tk
import random
import math

# ── Window settings ──────────────────────────────────────────────────────────
WIN_W   = 300
WIN_H   = 140
BG      = "#010d1a"          # deep-ocean dark
FG_FISH = "#7fffd4"          # aquamarine
FG_SEAG = "#2d8f6f"          # sea-green
FG_BUBBL= "#a0cfff"          # pale blue
FG_SAND = "#c8a96e"          # sandy beige
FONT    = ("Courier New", 13, "bold")
FONT_SM = ("Courier New", 10)
TICK_MS = 60                 # animation frame ms  (~16 fps)

# ── Fish designs ─────────────────────────────────────────────────────────────
FISH_RIGHT = [
    "><(((º>",
    "><>",
    "≋><(((º>",
    "><(((*>",
]
FISH_LEFT = [
    "<º)))><",
    "<><",
    "<º)))><≋",
    "<*(((><",
]

# ── Seagrass frames (3-frame wave) ───────────────────────────────────────────
GRASS_FRAMES = [
    ["  |  ", " \\|  ", "  |/ "],
    [" \\|  ", "  |  ", "  |/ "],
    ["  |/ ", "  |  ", " \\|  "],
]

# ── Bubble pattern ────────────────────────────────────────────────────────────
BUBBLES = ["o", "O", "°", "·", "ø"]


class Fish:
    def __init__(self, canvas_w, canvas_h, floor_y):
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h
        self.floor_y  = floor_y
        self._spawn()

    def _spawn(self):
        idx = random.randint(0, len(FISH_RIGHT) - 1)
        self.right_str = FISH_RIGHT[idx]
        self.left_str  = FISH_LEFT[idx]

        self.going_right = random.choice([True, False])
        self.y = random.randint(40, self.floor_y - 60)
        self.speed = random.uniform(1.2, 3.5)
        self.wobble_amp   = random.uniform(0, 12)
        self.wobble_freq  = random.uniform(0.04, 0.10)
        self.wobble_phase = random.uniform(0, math.tau)
        self.t = 0

        # colour tints
        tints = ["#7fffd4", "#98fb98", "#fffacd", "#f0e68c",
                 "#b0e0e6", "#dda0dd", "#ffa07a", "#add8e6"]
        self.color = random.choice(tints)

        if self.going_right:
            self.x = -len(self.right_str) * 9
        else:
            self.x = self.canvas_w + len(self.left_str) * 9

        self.cur_y = float(self.y)  # initialise before first step()

    def step(self):
        self.t += 1
        dy = self.wobble_amp * math.sin(self.wobble_freq * self.t + self.wobble_phase)

        if self.going_right:
            self.x += self.speed
            if self.x > self.canvas_w + 80:
                self._spawn()
        else:
            self.x -= self.speed
            if self.x < -120:
                self._spawn()

        self.cur_y = self.y + dy

    @property
    def text(self):
        return self.right_str if self.going_right else self.left_str


class Bubble:
    def __init__(self, canvas_w, floor_y):
        self.canvas_w = canvas_w
        self.floor_y  = floor_y
        self._spawn()

    def _spawn(self):
        self.x    = float(random.randint(10, self.canvas_w - 10))
        self.y    = float(self.floor_y - random.randint(0, 30))
        self.char = random.choice(BUBBLES)
        self.speed= random.uniform(0.4, 1.2)
        self.drift= random.uniform(-0.3, 0.3)
        self.life = 0
        self.max_life = random.randint(80, 200)

    def step(self):
        self.y    -= self.speed
        self.x    += self.drift
        self.life += 1
        if self.life > self.max_life or self.y < 0:
            self._spawn()


class SeaGrass:
    def __init__(self, x, height, canvas_h, floor_y):
        self.x       = x
        self.height  = height        # number of segments
        self.floor_y = floor_y
        self.canvas_h= canvas_h
        self.frame   = random.randint(0, 2)
        self.tick    = 0
        self.rate    = random.randint(8, 18)  # frames between animation steps
        self.color   = random.choice(["#2d8f6f", "#3ab87e", "#1a6b50", "#55c08a"])

    def step(self):
        self.tick += 1
        if self.tick >= self.rate:
            self.tick  = 0
            self.frame = (self.frame + 1) % 3

    def segments(self):
        """Return list of (char, x_offset, y) for each grass segment."""
        segs = []
        base_y = self.floor_y
        for i in range(self.height):
            frame_chars = GRASS_FRAMES[self.frame]
            ch = frame_chars[i % len(frame_chars)].strip() or "|"
            y  = base_y - i * 14
            segs.append((ch, y))
        return segs


class Aquarium:
    def __init__(self, root):
        self.root = root
        root.title("🐠 ASCII Aquarium")
        root.resizable(False, False)
        root.configure(bg=BG)

        # Centre window on screen
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        xo = (sw - WIN_W) // 2
        yo = (sh - WIN_H) // 2
        root.geometry(f"{WIN_W}x{WIN_H}+{xo}+{yo}")

        # Canvas
        self.canvas = tk.Canvas(root, width=WIN_W, height=WIN_H,
                                bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.floor_y = WIN_H - 40   # y-position of the sandy floor

        # ── Entities ──────────────────────────────────────────────────────────
        num_fish    = 3
        num_bubbles = 4
        num_grass   = 2

        self.fishes  = [Fish(WIN_W, WIN_H, self.floor_y)  for _ in range(num_fish)]
        self.bubbles = [Bubble(WIN_W, self.floor_y)        for _ in range(num_bubbles)]

        self.grasses = []
        used_x = set()
        for _ in range(num_grass):
            while True:
                gx = random.randint(20, WIN_W - 20)
                if all(abs(gx - u) > 25 for u in used_x):
                    break
            used_x.add(gx)
            gh = random.randint(3, 9)
            self.grasses.append(SeaGrass(gx, gh, WIN_H, self.floor_y))

        # Pre-draw static background gradient bands
        self._draw_background()

        # Canvas item handles (created once, then updated via coords/itemconfig)
        self.fish_ids   = []
        self.bubble_ids = []
        self.grass_ids  = {}   # grass index -> list of text-item ids

        self._create_items()
        self._animate()

    # ── Background ────────────────────────────────────────────────────────────
    def _draw_background(self):
        # Gradient bands (dark to slightly lighter blue top-to-bottom)
        bands = 12
        for i in range(bands):
            c  = int(1 + i * 12)
            c2 = int(13 + i * 5)
            colour = f"#{c:02x}{c2:02x}{min(0xff, 40 + i*12):02x}"
            y0 = i * (self.floor_y // bands)
            y1 = (i + 1) * (self.floor_y // bands)
            self.canvas.create_rectangle(0, y0, WIN_W, y1, fill=colour, outline="")

        # Sandy floor
        self.canvas.create_rectangle(0, self.floor_y, WIN_W, WIN_H,
                                     fill="#1a1200", outline="")
        # Sand ripples
        for sx in range(0, WIN_W, 22):
            sy = self.floor_y + random.randint(2, 12)
            self.canvas.create_text(sx, sy, text="~",
                                    fill=FG_SAND, font=FONT_SM, anchor="w")
        # Title
        self.canvas.create_text(WIN_W // 2, 14,
                                text="~ ASCII Aquarium ~",
                                fill="#7fffd4", font=("Courier New", 14, "bold"))

    # ── Create canvas items ───────────────────────────────────────────────────
    def _create_items(self):
        for f in self.fishes:
            iid = self.canvas.create_text(
                f.x, f.cur_y, text=f.text,
                fill=f.color, font=FONT, anchor="w")
            self.fish_ids.append(iid)

        for b in self.bubbles:
            iid = self.canvas.create_text(
                b.x, b.y, text=b.char,
                fill=FG_BUBBL, font=FONT_SM, anchor="center")
            self.bubble_ids.append(iid)

        for gi, g in enumerate(self.grasses):
            segs = g.segments()
            ids  = []
            for ch, y in segs:
                iid = self.canvas.create_text(
                    g.x, y, text=ch,
                    fill=g.color, font=FONT_SM, anchor="center")
                ids.append(iid)
            self.grass_ids[gi] = ids

    # ── Animation loop ────────────────────────────────────────────────────────
    def _animate(self):
        # Step all entities
        for f in self.fishes:
            f.step()
        for b in self.bubbles:
            b.step()
        for g in self.grasses:
            g.step()

        # Update fish
        for iid, f in zip(self.fish_ids, self.fishes):
            self.canvas.coords(iid, f.x, f.cur_y)
            self.canvas.itemconfig(iid, text=f.text)

        # Update bubbles
        for iid, b in zip(self.bubble_ids, self.bubbles):
            self.canvas.coords(iid, b.x, b.y)
            self.canvas.itemconfig(iid, text=b.char)

        # Update grass
        for gi, g in enumerate(self.grasses):
            segs = g.segments()
            ids  = self.grass_ids[gi]
            # Resize if needed (shouldn't change but just in case)
            for j, (ch, y) in enumerate(segs):
                if j < len(ids):
                    self.canvas.itemconfig(ids[j], text=ch)
                    self.canvas.coords(ids[j], g.x, y)

        self.root.after(TICK_MS, self._animate)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = Aquarium(root)
    root.mainloop()
