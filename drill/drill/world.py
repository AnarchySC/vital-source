"""Random but believable files and folders for scenarios."""

from pathlib import Path

GAMES = [
    "orbit-racer", "salvage-run", "neon-drift", "star-hauler", "void-tag", "relay-nine",
    "deep-signal", "comet-cafe", "dust-runner", "night-freight", "ion-storm", "cold-harbor",
]
MODS = ["better-lights", "fast-travel", "retro-hud", "big-maps", "night-mode", "extra-ships"]
SPRITES = ["ship", "asteroid", "pilot", "station", "cargo", "drone", "beacon", "wreck"]
SOUNDS = ["engine", "laser", "dock", "alarm", "warp", "pickup", "thruster"]
MAPS = ["belt", "nebula", "outpost", "canyon", "harbor", "ring", "shipyard"]
WORDS = [
    "signal", "orbit", "cargo", "drift", "relay", "beacon", "vector", "static", "hull",
    "comet", "ember", "harbor", "neon", "tape", "radar", "pulse", "ridge", "salvage",
]


def touch(path: Path, text: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def filler(rng, lines=None):
    n = lines or rng.randint(2, 8)
    return "".join(" ".join(rng.choice(WORDS) for _ in range(rng.randint(3, 9))) + "\n" for _ in range(n))


def game_tree(rng, root: Path):
    """One game folder with the usual layout; returns every directory created."""
    dirs = []

    def mk(*parts):
        d = root.joinpath(*parts)
        d.mkdir(parents=True, exist_ok=True)
        dirs.append(d)
        return d

    mk()
    for s in rng.sample(SPRITES, 3):
        touch(mk("assets", "sprites") / f"{s}.png", filler(rng))
    for s in rng.sample(SOUNDS, 2):
        touch(mk("assets", "sounds") / f"{s}.ogg", filler(rng))
    for m in rng.sample(MAPS, 2):
        touch(mk("assets", "maps") / f"{m}.map", filler(rng))
    for i in range(1, rng.randint(2, 4)):
        touch(mk("saves", f"slot-{i}") / "save.dat", filler(rng))
    touch(mk("config") / "settings.ini", filler(rng))
    touch(mk("logs") / "game.log", filler(rng, 20))
    for m in rng.sample(MODS, rng.randint(1, 2)):
        touch(mk("mods", m) / "mod.toml", filler(rng))
    touch(root / "README.md", filler(rng))
    return dirs


def world(rng, lab: Path, games=3):
    """A few game folders under ~/lab/games. Returns (game roots, all dirs)."""
    names = rng.sample(GAMES, games)
    roots, dirs = [], []
    for name in names:
        root = lab / "games" / name
        roots.append(root)
        dirs += game_tree(rng, root)
    return roots, dirs


def snapshot(root: Path) -> dict:
    """Relative path -> text for every file under root."""
    return {str(p.relative_to(root)): p.read_text() for p in sorted(root.rglob("*")) if p.is_file()}


def matches(root: Path, snap: dict) -> bool:
    try:
        return snapshot(root) == snap
    except (OSError, UnicodeDecodeError):
        return False
