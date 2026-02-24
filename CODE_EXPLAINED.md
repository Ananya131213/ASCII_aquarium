# 🐠 ASCII Aquarium — Code Explained

## Overview

`aquarium.py` is a self-contained Python animation built with **tkinter**. It opens a mini window and uses a canvas to draw and continuously update ASCII text characters, creating the illusion of a living underwater scene.

---

## 1. Configuration Constants

```python
WIN_W, WIN_H = 900, 420   # Window dimensions (pixels)
BG           = "#010d1a"  # Dark ocean background colour
TICK_MS      = 60         # Milliseconds between frames (~16 fps)
```

These top-level constants act as a central control panel — changing them adjusts the whole scene without touching any class logic.

---

## 2. ASCII Art Data

```python
FISH_RIGHT = ["><(((º>", "><>", ...]
FISH_LEFT  = ["<º)))><", "<><", ...]

GRASS_FRAMES = [[...], [...], [...]]   # 3 animation frames per grass stalk
BUBBLES      = ["o", "O", "°", "·", "ø"]
```

- **`FISH_RIGHT` / `FISH_LEFT`** — Mirror-image pairs of ASCII fish strings. When a fish swims left, its left-facing string is shown; when it turns right, the right-facing one is used.
- **`GRASS_FRAMES`** — A list of 3 frames, each containing a set of character variants (`|`, `\|`, `|/`) that cycle to simulate swaying.
- **`BUBBLES`** — Different-sized bubble characters that rise from the seafloor.

---

## 3. The `Fish` Class

Represents one swimming fish entity.

| Method | Purpose |
|--------|---------|
| `__init__` | Stores canvas dimensions, calls `_spawn()` |
| `_spawn()` | Picks a random fish design, direction, speed, wobble settings, colour, and starting position off-screen |
| `step()` | Advances position each frame; applies a **sine-wave wobble** (`sin`) for vertical undulation; re-spawns if fish exits canvas |
| `text` (property) | Returns the correct ASCII string based on current swim direction |

**Key animation idea — wobble:**
```python
dy = self.wobble_amp * math.sin(self.wobble_freq * self.t + self.wobble_phase)
self.cur_y = self.y + dy
```
Each fish has unique amplitude, frequency, and phase, so no two fish bob identically.

---

## 4. The `Bubble` Class

Represents a single rising bubble.

| Method | Purpose |
|--------|---------|
| `_spawn()` | Places the bubble at a random x position near the seafloor |
| `step()` | Moves bubble upward (`y -= speed`) with a slight horizontal drift; re-spawns when it exits or exceeds its max lifetime |

Bubbles have a **lifetime** counter so they naturally fade out and reappear elsewhere, keeping the scene fresh.

---

## 5. The `SeaGrass` Class

Represents one vertical stalk of seagrass rooted in the sandy floor.

| Attribute | Purpose |
|-----------|---------|
| `height` | Number of character segments tall the stalk is |
| `frame` | Current waving frame index (0, 1, or 2) |
| `rate` | How many ticks between frame changes (randomised per stalk) |

| Method | Purpose |
|--------|---------|
| `step()` | Increments a tick counter; advances `frame` every `rate` ticks |
| `segments()` | Returns a list of `(character, y_position)` tuples for each stalk segment, read from `GRASS_FRAMES` |

Because each stalk has a different `rate`, they sway out of phase with each other, which looks natural.

---

## 6. The `Aquarium` Class (Main Controller)

This class owns the tkinter window, the canvas, and all entities.

### `__init__`
- Creates and centres the window on screen.
- Instantiates all `Fish`, `Bubble`, and `SeaGrass` objects.
- Calls `_draw_background()` then `_create_items()`, then starts the loop with `_animate()`.

### `_draw_background()`
Draws **12 gradient rectangle bands** from dark navy at the top to slightly lighter blue near the floor, giving depth. Also draws:
- A static sandy floor rectangle.
- Randomised `~` characters as sand ripples.
- A title label at the top.

These are drawn once and never redrawn — they stay under all animated elements.

### `_create_items()`
Creates **tkinter canvas text items** for every fish, bubble, and grass segment. Each item gets an integer ID so it can be updated efficiently later — no items are destroyed and recreated each frame.

```python
iid = self.canvas.create_text(x, y, text="...", fill="...", font=...)
```

### `_animate()` — The Animation Loop
Called every `TICK_MS` milliseconds via `root.after(...)`.

```
Each frame:
  1. Call .step() on every Fish, Bubble, SeaGrass
  2. Update canvas items:
       canvas.coords(id, new_x, new_y)   ← moves the text item
       canvas.itemconfig(id, text=...)   ← changes the character string
  3. Schedule the next frame: root.after(TICK_MS, self._animate)
```

Using `coords` + `itemconfig` instead of deleting/re-creating items is the key performance trick — tkinter can update existing items much faster than creating new ones each frame.

---

## 7. Entry Point

```python
if __name__ == "__main__":
    root = tk.Tk()
    app  = Aquarium(root)
    root.mainloop()
```

Standard tkinter pattern: create the root window, hand it to the `Aquarium` controller, then start the event loop.

---

## Data Flow Summary

```
root.after(60ms)
      │
      ▼
  _animate()
      │
      ├─ fish.step()   → updates fish.x, fish.cur_y
      ├─ bubble.step() → updates bubble.x, bubble.y
      └─ grass.step()  → advances grass.frame
      │
      ├─ canvas.coords / itemconfig  ← Fish items
      ├─ canvas.coords / itemconfig  ← Bubble items
      └─ canvas.coords / itemconfig  ← Grass items
```

All animation happens inside a single `after` callback — no threads required.
