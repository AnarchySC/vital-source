import os

from .. import world
from ..engine import Exercise, Lesson, Result

INTRO = """
Everything on Linux lives somewhere in one big tree of folders, and your terminal is
always standing in exactly one of them. Most "it says no such file" moments are really
"I'm not where I think I am."

    `pwd`          where am I?
    `ls`           what's here?          `ls -la`   everything, hidden too, with details
    `cd games`     go into games         `cd ..`    go up one level
    `cd ~`         go home               `cd -`     go back to where you just were

A path that starts with / is absolute: the full address from the top of the tree,
like `/home/learner/lab`. A path that starts with ~ starts at your home folder. Anything
else is relative: it starts from where you're standing right now.

Your prompt shows where you are, too. Press Tab to finish folder names for you.
"""

UPS = {1: "one folder up", 2: "two folders up", 3: "three folders up"}


def same_dir(cwd, target):
    return cwd is not None and os.path.realpath(cwd) == os.path.realpath(target)


class GoTo(Exercise):
    id = "nav.goto"
    title = "Go straight there"
    target = 25

    def setup(self, rng, ctx):
        roots, dirs = world.world(rng, ctx.lab)
        deep = [d for d in dirs if len(d.relative_to(ctx.lab).parts) >= 4]
        dest = rng.choice(deep)
        what = {"sprites": "the sprite art", "sounds": "the sound effects", "maps": "the map files",
                "config": "the settings"}.get(dest.name, "the files support asked for")
        prompt = (f"Support needs you to look at {what} for {dest.relative_to(ctx.lab / 'games').parts[0]}. "
                  f"They're in:\n\n    {ctx.show(dest)}\n\nGo there.")
        return {"dest": str(dest), "start": str(ctx.home), "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        if same_dir(cwd, st["dest"]):
            return Result(True)
        return Result(False, f"You're in {ctx.show(cwd) if cwd else 'a folder that no longer exists'}, "
                             f"not {ctx.show(st['dest'])}.")

    def hint(self, st, ctx):
        return f"`cd {ctx.show(st['dest'])}`\n\nType the first few letters of each folder and press Tab."


class Relative(Exercise):
    id = "nav.relative"
    title = "Directions, not addresses"
    target = 25

    def setup(self, rng, ctx):
        roots, dirs = world.world(rng, ctx.lab)
        while True:
            start = rng.choice([d for d in dirs if len(d.relative_to(ctx.lab).parts) >= 4])
            up = rng.randint(1, 3)
            base = start.parents[up - 1]
            if ctx.lab / "games" not in base.parents:
                continue
            options = [d for d in dirs if base in d.parents and d != start and start not in d.parents
                       and d not in start.parents and 1 <= len(d.relative_to(base).parts) <= 2]
            if options:
                break
        dest = rng.choice(options)
        down = str(dest.relative_to(base))
        prompt = (f"You're in `{ctx.show(start)}`. A teammate says what you need is "
                  f"\"{UPS[up]}, then in {down}\".\n\nGet there without typing the full path.")
        return {"start": str(start), "dest": str(dest), "up": up, "down": down, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        if same_dir(cwd, st["dest"]):
            return Result(True, f"`cd {'../' * st['up']}{st['down']}` gets there in one line.")
        return Result(False, f"You're in {ctx.show(cwd) if cwd else 'a folder that no longer exists'}, "
                             f"not {ctx.show(st['dest'])}.")

    def hint(self, st, ctx):
        return (f".. means one folder up. Chain them, then keep going down:\n\n"
                f"    `cd {'../' * st['up']}{st['down']}`")


class FullPath(Exercise):
    id = "nav.fullpath"
    title = "Give the full path"
    target = 30
    answer = True

    def setup(self, rng, ctx):
        roots, dirs = world.world(rng, ctx.lab)
        here = rng.choice([d for d in dirs if any(p.is_file() for p in d.iterdir())])
        file = rng.choice([p for p in here.iterdir() if p.is_file()])
        prompt = (f"A mod installer wants the full path to `{file.name}`, the file in the "
                  f"folder you're standing in. It won't accept a relative path, and it won't "
                  f"understand ~ either: it has to start with /.\n\nSend the full path.")
        return {"start": str(here), "file": str(file), "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        a = (answer or "").strip().strip("'\"")
        if not a.startswith("/"):
            return Result(False, "A full path starts with /. `pwd` prints the one for where you are.")
        if os.path.realpath(a) == os.path.realpath(st["file"]):
            return Result(True)
        if os.path.realpath(a) == os.path.realpath(st["start"]):
            return Result(False, "That's the folder. Add the file name on the end.")
        return Result(False, "That path doesn't lead to the file.")

    def hint(self, st, ctx):
        return f"`pwd` prints the folder. Put / and the file name after it."


class Hidden(Exercise):
    id = "nav.hidden"
    title = "Find what's hidden"
    target = 30
    answer = True

    def setup(self, rng, ctx):
        roots, dirs = world.world(rng, ctx.lab, games=2)
        root = rng.choice(roots)
        name = "." + rng.choice(["profile", "secrets", "unlocks", "cheats", "keys", "achievements"]) \
            + rng.choice(["", ".dat", ".json", "-v2"])
        world.touch(root / name, world.filler(rng))
        prompt = (f"{root.name} keeps a file in `{ctx.show(root)}` that you can't see with a "
                  f"plain `ls`. On Linux, any file whose name starts with a dot is hidden.\n\n"
                  f"Send its name.")
        return {"dir": str(root), "name": name, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        a = (answer or "").strip().strip("'\"")
        a = a[2:] if a.startswith("./") else a
        if a == st["name"]:
            return Result(True)
        if "." + a == st["name"]:
            return Result(False, "Close. The dot is part of the name; include it.")
        return Result(False, "That's not it.")

    def hint(self, st, ctx):
        return f"-a means all, hidden ones too:\n\n    `ls -a {ctx.show(st['dir'])}`"


class WhichDir(Exercise):
    id = "nav.whichdir"
    title = "File or folder?"
    target = 30
    answer = True

    def setup(self, rng, ctx):
        root = ctx.lab / "inbox"
        names = rng.sample(["notes.txt", "backup.zip", "photo.png", "song.mp3", "plan.md",
                            "level.map", "save.dat", "manual.pdf", "trailer.mp4", "patch.deb"], 7)
        disguised = names[0]
        (root / disguised).mkdir(parents=True)
        world.touch(root / disguised / "README", world.filler(rng))
        for n in names[1:]:
            world.touch(root / n, world.filler(rng))
        prompt = (f"Something in `{ctx.show(root)}` won't open. The name says it's a file, but "
                  f"one of these is really a folder with a misleading name.\n\nSend the name of "
                  f"the folder.")
        return {"dir": str(root), "name": disguised, "prompt": prompt}

    def check(self, st, ctx, cwd, answer):
        a = (answer or "").strip().strip("'\"").rstrip("/")
        if a == st["name"]:
            return Result(True)
        return Result(False, f"{a or 'That'} is a regular file.")

    def hint(self, st, ctx):
        return (f"In `ls -l {ctx.show(st['dir'])}`, lines that start with d are folders "
                f"(directories). `ls -F` puts a / after folder names instead.")


LESSON = Lesson(
    number=1,
    name="Navigate",
    hook="Where am I, and how do I get there?",
    intro=INTRO,
    exercises=[GoTo(), Relative(), FullPath(), Hidden(), WhichDir()],
)
